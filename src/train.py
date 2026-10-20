"""src/train.py — GlucoTwin two-hour glucose forecasting baseline."""

import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import GroupShuffleSplit
from sklearn.pipeline import Pipeline

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
MODELS = ROOT / "models"

HORIZON_STEPS = 24  # 24 x 5 minutes = 2 hours
SEED = 42


def load_data():
    ehr = pd.read_csv(DATA / "ehr.csv")
    sensor = pd.read_csv(
        DATA / "sensor_readings.csv",
        parse_dates=["timestamp"],
    )

    required_ehr = {
        "patient_id", "age", "bmi", "hba1c",
        "years_since_diagnosis", "hypertension", "ckd",
        "metformin", "sglt2i", "sulfonylurea", "insulin",
    }
    required_sensor = {
        "patient_id", "timestamp", "glucose_mgdl",
        "heart_rate_bpm", "steps", "is_asleep",
    }

    if not required_ehr.issubset(ehr.columns):
        raise ValueError("Missing required EHR columns.")
    if not required_sensor.issubset(sensor.columns):
        raise ValueError("Missing required sensor columns.")
    if ehr["patient_id"].duplicated().any():
        raise ValueError("EHR must have one row per patient.")
    if ehr["patient_id"].isna().any():
        raise ValueError("EHR contains missing patient IDs.")
    if sensor["patient_id"].isna().any():
        raise ValueError("Sensor data contains missing patient IDs.")

    sensor = sensor.sort_values(
        ["patient_id", "timestamp"]
    ).reset_index(drop=True)

    # Require one reading per patient per timestamp.
    if sensor.duplicated(["patient_id", "timestamp"]).any():
        raise ValueError("Duplicate patient timestamps detected.")

    unknown = set(sensor["patient_id"]) - set(ehr["patient_id"])
    if unknown:
        raise ValueError("Some sensor patient IDs have no EHR record.")

    # Merge static patient attributes into every sensor observation.
    df = sensor.merge(
        ehr,
        on="patient_id",
        how="left",
        validate="many_to_one",
    )

    # Encode sex numerically.
    df["sex_male"] = df["sex"].map({"F": 0, "M": 1})
    if df["sex_male"].isna().any():
        raise ValueError("Unexpected or missing sex values in EHR.")

    return df


def make_features(df):
    df = df.copy()
    groups = df.groupby("patient_id", sort=False)

    # Current and historical glucose readings.
    for lag in [3, 6, 12, 24]:
        df[f"glucose_lag_{lag}"] = groups[
            "glucose_mgdl"
        ].shift(lag)

    # Rolling features use current and past observations only.
    for window in [6, 12]:
        df[f"glucose_mean_{window}"] = (
            df.groupby("patient_id", sort=False)["glucose_mgdl"]
            .transform(
                lambda s: s.rolling(
                    window=window, min_periods=1
                ).mean()
            )
        )

    df["glucose_change_30m"] = (
        df["glucose_mgdl"] - df["glucose_lag_6"]
    )

    df["heart_rate_mean_30m"] = (
        df.groupby("patient_id", sort=False)["heart_rate_bpm"]
        .transform(
            lambda s: s.rolling(
                window=6, min_periods=1
            ).mean()
        )
    )

    df["steps_sum_30m"] = (
        df.groupby("patient_id", sort=False)["steps"]
        .transform(
            lambda s: s.rolling(
                window=6, min_periods=1
            ).sum()
        )
    )

    # Time-of-day features.
    hour = (
        df["timestamp"].dt.hour
        + df["timestamp"].dt.minute / 60
    )
    df["hour_sin"] = np.sin(2 * np.pi * hour / 24)
    df["hour_cos"] = np.cos(2 * np.pi * hour / 24)

    # Future target: glucose 2 hours after the current timestamp.
    df["target_glucose_2h"] = (
        df.groupby("patient_id", sort=False)["glucose_mgdl"]
        .shift(-HORIZON_STEPS)
    )

    features = [
        "age", "sex_male", "bmi", "years_since_diagnosis",
        "hba1c", "hypertension", "ckd", "metformin",
        "sglt2i", "sulfonylurea", "insulin",
        "glucose_mgdl", "glucose_lag_3", "glucose_lag_6",
        "glucose_lag_12", "glucose_lag_24",
        "glucose_mean_6", "glucose_mean_12",
        "glucose_change_30m", "heart_rate_bpm",
        "heart_rate_mean_30m", "steps", "steps_sum_30m",
        "is_asleep", "hour_sin", "hour_cos",
    ]

    # Do not train on rows without a future glucose target.
    df = df.dropna(subset=["target_glucose_2h"]).copy()

    return df, features


def main():
    MODELS.mkdir(parents=True, exist_ok=True)

    df = load_data()
    df, features = make_features(df)

    # Group split keeps all rows for each patient in either train or test.
    splitter = GroupShuffleSplit(
        n_splits=1,
        test_size=0.2,
        random_state=SEED,
    )
    train_idx, test_idx = next(
        splitter.split(df, groups=df["patient_id"])
    )

    train_df = df.iloc[train_idx].copy()
    test_df = df.iloc[test_idx].copy()

    X_train = train_df[features]
    y_train = train_df["target_glucose_2h"]
    X_test = test_df[features]
    y_test = test_df["target_glucose_2h"]

    pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        (
            "model",
            RandomForestRegressor(
                n_estimators=100,
                max_depth=16,
                min_samples_leaf=5,
                random_state=SEED,
                n_jobs=-1,
            ),
        ),
    ])

    pipeline.fit(X_train, y_train)
    predictions = pipeline.predict(X_test)

    # Persistence baseline assumes future glucose equals current glucose.
    # Exclude test rows missing current glucose from the baseline evaluation.
    valid = test_df["glucose_mgdl"].notna()
    baseline_mae = float(
        mean_absolute_error(
            y_test[valid],
            test_df.loc[valid, "glucose_mgdl"],
        )
    )

    mae = float(mean_absolute_error(y_test, predictions))
    rmse = float(np.sqrt(mean_squared_error(y_test, predictions)))
    r2 = float(r2_score(y_test, predictions))

    metrics = {
        "horizon_minutes": HORIZON_STEPS * 5,
        "patients_total": int(df["patient_id"].nunique()),
        "train_patients": int(train_df["patient_id"].nunique()),
        "test_patients": int(test_df["patient_id"].nunique()),
        "train_rows": int(len(train_df)),
        "test_rows": int(len(test_df)),
        "model_mae_mg_dl": round(mae, 3),
        "model_rmse_mg_dl": round(rmse, 3),
        "model_r2": round(r2, 4),
        "persistence_baseline_mae_mg_dl": round(baseline_mae, 3),
        "synthetic_data_only": True,
    }

    model_path = MODELS / "glucose_model.joblib"
    joblib.dump(
        {
            "model": pipeline,
            "features": features,
            "horizon_minutes": HORIZON_STEPS * 5,
        },
        model_path,
        compress=3,
    )

    metrics_path = MODELS / "metrics.json"
    with open(metrics_path, "w") as f:
        json.dump(metrics, f, indent=2)

    result_path = MODELS / "result.txt"
    with open(result_path, "w") as f:
        f.write(
            f"GlucoTwin 2-hour forecast evaluation:\n"
            f"  Train patients: {metrics['train_patients']}\n"
            f"  Test patients:  {metrics['test_patients']}\n"
            f"  Model MAE:      {metrics['model_mae_mg_dl']:.2f} mg/dL\n"
            f"  Model RMSE:     {metrics['model_rmse_mg_dl']:.2f} mg/dL\n"
            f"  Model R2:       {metrics['model_r2']:.4f}\n"
            f"  Baseline MAE:   {metrics['persistence_baseline_mae_mg_dl']:.2f} mg/dL\n"
        )

    print("Training complete.")
    print(f"Model saved to:   {model_path}")
    print(f"Metrics saved to: {metrics_path}")
    print(f"Summary saved to: {result_path}")
    print(
        f"Model MAE: {mae:.2f} mg/dL vs "
        f"Baseline: {baseline_mae:.2f} mg/dL "
        f"({100 * (baseline_mae - mae) / baseline_mae:.1f}% improvement)"
    )


if __name__ == "__main__":
    main()

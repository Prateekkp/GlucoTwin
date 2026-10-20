"""Clinical feature extraction, phenotypic classification, and counterfactual transformations."""

import numpy as np
import pandas as pd

from src.config import ICMR_OVERWEIGHT_BMI, ICMR_OBESE_BMI


def get_bmi_classification(bmi: float) -> str:
    """Classify Body Mass Index using ICMR-INDIAB South Asian cutoffs."""
    if bmi >= ICMR_OBESE_BMI:
        return "Obese (ICMR)"
    elif bmi >= ICMR_OVERWEIGHT_BMI:
        return "Overweight (ICMR)"
    elif bmi >= 18.5:
        return "Normal Weight"
    else:
        return "Underweight"


def _get_lag(series: pd.Series, lag: int) -> float:
    """Retrieve historical value at lag steps from the end of the series."""
    return float(series.iloc[-1 - lag]) if len(series) > lag else np.nan


def extract_twin_features(
    patient: pd.Series, visible_sensor: pd.DataFrame, features: list
) -> tuple[dict, pd.DataFrame]:
    """Fuse static EHR attributes with dynamic sensor window to construct model feature vector."""
    current = visible_sensor.iloc[-1]
    glucose_series = visible_sensor["glucose_mgdl"]
    hr_series = visible_sensor["heart_rate_bpm"]
    steps_series = visible_sensor["steps"]

    row = patient.to_dict()
    row["sex_male"] = int(patient["sex"] == "M")
    row["glucose_mgdl"] = current["glucose_mgdl"]
    row["glucose_lag_3"] = _get_lag(glucose_series, 3)
    row["glucose_lag_6"] = _get_lag(glucose_series, 6)
    row["glucose_lag_12"] = _get_lag(glucose_series, 12)
    row["glucose_lag_24"] = _get_lag(glucose_series, 24)
    row["glucose_mean_6"] = float(glucose_series.tail(6).mean())
    row["glucose_mean_12"] = float(glucose_series.tail(12).mean())
    row["glucose_change_30m"] = (
        float(current["glucose_mgdl"] - row["glucose_lag_6"])
        if pd.notna(row["glucose_lag_6"])
        else 0.0
    )
    row["heart_rate_bpm"] = current["heart_rate_bpm"]
    row["heart_rate_mean_30m"] = float(hr_series.tail(6).mean())
    row["steps"] = current["steps"]
    row["steps_sum_30m"] = float(steps_series.tail(6).sum())
    row["is_asleep"] = int(current["is_asleep"])

    hour_val = current["timestamp"].hour + current["timestamp"].minute / 60.0
    row["hour_sin"] = float(np.sin(2 * np.pi * hour_val / 24))
    row["hour_cos"] = float(np.cos(2 * np.pi * hour_val / 24))

    X = pd.DataFrame(
        [[row.get(f, np.nan) for f in features]],
        columns=features,
    )
    return row, X


def build_counterfactual_features(
    base_row: dict,
    activity_option: str,
    med_option: str,
    nutrition_option: str,
    features: list,
) -> tuple[dict, pd.DataFrame]:
    """Construct modified feature vector simulating prospective physician interventions."""
    row_cf = base_row.copy()

    # Activity Interventions
    if "15-Minute" in activity_option:
        row_cf["steps"] += 1000
        row_cf["steps_sum_30m"] += 1000
        row_cf["glucose_change_30m"] -= 12.0
    elif "30-Minute" in activity_option:
        row_cf["steps"] += 2500
        row_cf["steps_sum_30m"] += 2500
        row_cf["glucose_change_30m"] -= 25.0

    # Medication Adherence / Titration
    if "SGLT2i" in med_option:
        row_cf["sglt2i"] = 1
        row_cf["glucose_change_30m"] -= 10.0
    elif "Correction Insulin" in med_option:
        row_cf["insulin"] = 1
        row_cf["glucose_change_30m"] -= 20.0

    # Dietary Carbohydrate Loads
    if "Low-Glycemic" in nutrition_option:
        row_cf["glucose_change_30m"] -= 15.0
    elif "High-Glycemic" in nutrition_option:
        row_cf["glucose_change_30m"] += 25.0

    X_cf = pd.DataFrame(
        [[row_cf.get(f, np.nan) for f in features]],
        columns=features,
    )
    return row_cf, X_cf


def calculate_agp_kpis(history_window: pd.DataFrame) -> dict:
    """Calculate Ambulatory Glucose Profile (AGP) and Time-In-Range (TIR) metrics."""
    n_pts = len(history_window)
    if n_pts == 0:
        return {
            "tir": 100.0,
            "tar": 0.0,
            "tbr": 0.0,
            "mean_g": 120.0,
            "std_g": 20.0,
            "cv_g": 16.7,
            "gmi": 6.2,
        }

    glucose = history_window["glucose_mgdl"]
    tir = float(100.0 * (glucose.between(70, 180)).sum() / n_pts)
    tar = float(100.0 * (glucose > 180).sum() / n_pts)
    tbr = float(100.0 * (glucose < 70).sum() / n_pts)
    mean_g = float(glucose.mean())
    std_g = float(glucose.std()) if n_pts > 1 else 0.0
    cv_g = float((std_g / mean_g * 100.0)) if mean_g > 0 else 0.0
    gmi = float(3.31 + (0.02392 * mean_g))

    return {
        "tir": tir,
        "tar": tar,
        "tbr": tbr,
        "mean_g": mean_g,
        "std_g": std_g,
        "cv_g": cv_g,
        "gmi": gmi,
    }

"""
generate_data.py - Synthetic EHR + CGM/wearable data for GlucoTwin.

Outputs:
  data/ehr.csv              one row per patient (static clinical profile)
  data/sensor_readings.csv  one row per patient every 5 minutes (CGM + wearable)

Glucose model (simplified, physiology-inspired):
  - Fasting baseline linked to HbA1c via the ADAG relation (mean glucose = 28.7*A1c - 46.7)
  - Meal excursions driven by carbohydrates, peaking ~45 min after eating
  - Dawn phenomenon (early-morning rise), weaker in insulin users
  - Medication effects: metformin, SGLT2 inhibitor, sulfonylurea, insulin
  - Post-dinner walks lower glucose
  - Autocorrelated physiological noise + CGM sensor noise + ~1.5% sensor dropouts

Heart rate depends on age, BMI, activity and sleep.

All data is SYNTHETIC and for research/demo purposes only. Not for clinical use.
"""
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "data"
OUT_DIR.mkdir(parents=True, exist_ok=True)

SEED = 42
N_PATIENTS = 120
DAYS = 14
STEP_MIN = 5
START = pd.Timestamp("2026-09-01 00:00:00")

rng = np.random.default_rng(SEED)

N_STEPS = DAYS * 24 * 60 // STEP_MIN
t_idx = np.arange(N_STEPS)
t_min = t_idx * STEP_MIN
abs_hours = t_min / 60.0
hour_of_day = abs_hours % 24

# ---------------- EHR (static profile) ----------------
ids = [f"P{i:04d}" for i in range(1, N_PATIENTS + 1)]
age = rng.integers(28, 81, N_PATIENTS)
sex = rng.choice(["F", "M"], N_PATIENTS, p=[0.48, 0.52])
bmi = np.clip(rng.normal(28.5, 4.5, N_PATIENTS), 19.0, 45.0).round(1)
years_dx = np.clip(rng.gamma(2.0, 4.0, N_PATIENTS), 0.5, 35.0).round(1)
hba1c = np.clip(
    rng.normal(7.6, 1.0, N_PATIENTS) + 0.03 * (bmi - 28.5) + 0.01 * (years_dx - 8),
    5.7, 13.5,
).round(1)
hypertension = (rng.random(N_PATIENTS) < 0.10 + 0.5 * (age - 28) / 52).astype(int)
ckd = (rng.random(N_PATIENTS) < 0.08).astype(int)
metformin = (rng.random(N_PATIENTS) < 0.85).astype(int)
sglt2i = (rng.random(N_PATIENTS) < 0.30 + 0.10 * (hba1c > 8.5)).astype(int)
sulfonylurea = (rng.random(N_PATIENTS) < 0.20).astype(int)
p_insulin = 1 / (1 + np.exp(-1.5 * (hba1c - 9.0)))
insulin = (rng.random(N_PATIENTS) < p_insulin).astype(int)

# ---------------- Per-patient physiology ----------------
fasting = 28.7 * hba1c - 46.7 - 20 + rng.normal(0, 6, N_PATIENTS)
fasting -= 15 * insulin + 8 * metformin + 10 * sglt2i + 6 * sulfonylurea
meal_gain = np.clip(rng.normal(0.8, 0.15, N_PATIENTS), 0.4, 1.4) * (0.7 + 0.15 * (hba1c - 6.0))
meal_gain = meal_gain * np.where(insulin == 1, 0.8, 1.0)
carb_scale = rng.uniform(0.8, 1.3, N_PATIENTS)
activity_level = rng.lognormal(0.0, 0.3, N_PATIENTS)
rhr_base = 62 + 0.12 * (age - 40) + 4 * (bmi > 30) + rng.normal(0, 3, N_PATIENTS)


def meal_response(dt, tau):
    """0 before the event, peaks at 1.0 when dt == tau, decays afterwards (cut off at 4 h)."""
    out = np.zeros_like(dt, dtype=float)
    m = (dt > 0) & (dt <= 240)
    x = dt[m] / tau
    out[m] = x * np.exp(1.0 - x)
    return out


sensor_frames = []
for p in range(N_PATIENTS):
    meal_times, meal_carbs = [], []
    walk_starts = []
    sleep_mask = np.zeros(N_STEPS, dtype=bool)

    for d in range(DAYS):
        base = d * 24 * 60
        if rng.random() > 0.10:  # 10% skip breakfast
            meal_times.append(base + 7.5 * 60 + rng.normal(0, 20))
            meal_carbs.append(max(10, rng.normal(45, 10)) * carb_scale[p])
        meal_times.append(base + 12.5 * 60 + rng.normal(0, 25))
        meal_carbs.append(max(15, rng.normal(70, 15)) * carb_scale[p])
        meal_times.append(base + 19.5 * 60 + rng.normal(0, 25))
        meal_carbs.append(max(15, rng.normal(75, 15)) * carb_scale[p])
        if rng.random() < 0.4:  # afternoon snack
            meal_times.append(base + 16 * 60 + rng.normal(0, 20))
            meal_carbs.append(max(5, rng.normal(25, 8)) * carb_scale[p])

        bed_h = d * 24 + rng.normal(23.0, 0.8)
        dur_h = np.clip(rng.normal(7.0, 0.8), 5.0, 9.5)
        sleep_mask |= (abs_hours >= bed_h) & (abs_hours < bed_h + dur_h)

        if rng.random() < 0.35:  # post-dinner walk
            walk_starts.append(base + 20.5 * 60 + rng.normal(0, 15))

    # Meal effect
    meal_effect = np.zeros(N_STEPS)
    for mt, mc in zip(meal_times, meal_carbs):
        meal_effect += mc * meal_gain[p] * meal_response(t_min - mt, tau=45)

    # Walk effect (lowers glucose)
    walk_effect = np.zeros(N_STEPS)
    walk_active = np.zeros(N_STEPS, dtype=bool)
    for ws in walk_starts:
        walk_effect += (12 + 8 * insulin[p]) * meal_response(t_min - ws, tau=30)
        walk_active |= (t_min >= ws) & (t_min < ws + 30)

    # Dawn phenomenon
    dawn = (4 if insulin[p] else 12) * np.exp(-((hour_of_day - 6.5) / 1.5) ** 2)

    # Autocorrelated physiological noise
    eps = rng.normal(0, 1.5, N_STEPS)
    ar = np.zeros(N_STEPS)
    for i in range(1, N_STEPS):
        ar[i] = 0.9 * ar[i - 1] + eps[i]

    glucose_true = fasting[p] + meal_effect - walk_effect - dawn + ar
    glucose_obs = np.clip(glucose_true + rng.normal(0, 2.0, N_STEPS), 40, 400).round()
    glucose_obs[rng.random(N_STEPS) < 0.015] = np.nan  # sensor dropouts

    # Wearable: steps
    lam = np.where((hour_of_day >= 7) & (hour_of_day < 22), 14.0, 0.3) * activity_level[p]
    steps = rng.poisson(lam) + walk_active * rng.poisson(95, N_STEPS)
    steps = np.where(sleep_mask, 0, steps)

    # Wearable: heart rate
    smooth_steps = np.convolve(steps, np.ones(3) / 3, mode="same")
    hr = rhr_base[p] + np.clip(smooth_steps * 0.3, 0, 45) - 8 * sleep_mask \
        + rng.normal(0, 2.5, N_STEPS)
    hr = np.clip(hr, 40, 190).round()
    hr[rng.random(N_STEPS) < 0.005] = np.nan

    sensor_frames.append(pd.DataFrame({
        "patient_id": ids[p],
        "timestamp": START + pd.to_timedelta(t_min, unit="m"),
        "glucose_mgdl": glucose_obs,
        "heart_rate_bpm": hr,
        "steps": steps.astype(int),
        "is_asleep": sleep_mask.astype(int),
    }))

ehr = pd.DataFrame({
    "patient_id": ids,
    "age": age,
    "sex": sex,
    "bmi": bmi,
    "years_since_diagnosis": years_dx,
    "hba1c": hba1c,
    "hypertension": hypertension,
    "ckd": ckd,
    "metformin": metformin,
    "sglt2i": sglt2i,
    "sulfonylurea": sulfonylurea,
    "insulin": insulin,
})
sensor = pd.concat(sensor_frames, ignore_index=True)

ehr.to_csv(OUT_DIR / "ehr.csv", index=False)
sensor.to_csv(OUT_DIR / "sensor_readings.csv", index=False, date_format="%Y-%m-%d %H:%M:%S")

# ---------------- Sanity report ----------------
g = sensor["glucose_mgdl"].dropna()
print(f"ehr.csv:              {len(ehr)} patients -> {OUT_DIR / 'ehr.csv'}")
print(f"sensor_readings.csv:  {len(sensor)} rows ({DAYS} days @ {STEP_MIN} min) -> {OUT_DIR / 'sensor_readings.csv'}")
print(f"Glucose mean/std:     {g.mean():.1f} / {g.std():.1f} mg/dL")
print(f"Time in range 70-180: {((g >= 70) & (g <= 180)).mean() * 100:.1f}%")
print(f"Time below 70:        {(g < 70).mean() * 100:.2f}%")
print(f"Time above 180:       {(g > 180).mean() * 100:.1f}%")
print(f"Glucose missing:      {sensor['glucose_mgdl'].isna().mean() * 100:.2f}%")
print(f"HbA1c range:          {hba1c.min()} - {hba1c.max()}")

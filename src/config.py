"""Configuration, system constants, and clinical thresholds for GlucoTwin."""

from pathlib import Path

# Paths
SRC_DIR = Path(__file__).resolve().parent
ROOT_DIR = SRC_DIR.parent
DATA_DIR = ROOT_DIR / "data"
MODELS_DIR = ROOT_DIR / "models"
MODEL_PATH = MODELS_DIR / "glucose_model.joblib"
METRICS_PATH = MODELS_DIR / "metrics.json"

# Clinical Thresholds (RSSDI / International Consensus)
HIGH_GLUCOSE_THRESHOLD = 180.0
LOW_GLUCOSE_THRESHOLD = 70.0

# Asian Indian Specific Phenotype Cutoffs (ICMR Guidelines)
ICMR_OVERWEIGHT_BMI = 23.0
ICMR_OBESE_BMI = 25.0

# Temporal Horizon
FORECAST_HORIZON_MINUTES = 120
STEP_MINUTES = 5
HORIZON_STEPS = FORECAST_HORIZON_MINUTES // STEP_MINUTES

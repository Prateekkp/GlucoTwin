"""Data and model loading utilities with Streamlit caching."""

import json
import joblib
import pandas as pd
import streamlit as st

from src.config import DATA_DIR, MODEL_PATH, METRICS_PATH


@st.cache_resource
def load_model():
    """Load the trained machine learning model artifact."""
    return joblib.load(MODEL_PATH)


@st.cache_data
def load_ehr():
    """Load synthetic EHR demographic and clinical cohort data."""
    return pd.read_csv(DATA_DIR / "ehr.csv")


@st.cache_data
def load_sensor():
    """Load continuous 5-minute CGM and wearable IoT sensor readings."""
    df = pd.read_csv(
        DATA_DIR / "sensor_readings.csv",
        parse_dates=["timestamp"],
    )
    return df.sort_values(["patient_id", "timestamp"]).reset_index(drop=True)


@st.cache_data
def load_metrics():
    """Load model validation benchmarks and evaluation statistics."""
    with open(METRICS_PATH) as f:
        return json.load(f)

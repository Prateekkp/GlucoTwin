"""GlucoTwin — Clinical Patient Digital Twin Platform.

Proactive Type 2 Diabetes Predictive Care & Adverse Event Early Warning System.
Developed for Happiest Health Reimagining and Reforming Healthcare in India Summit 2026.
"""

import streamlit as st

from src.styles import inject_custom_css
from src.data_loader import load_model, load_ehr, load_sensor, load_metrics
from src.features import get_bmi_classification
from src.views.landing_page import render_landing_page
from src.views.dashboard import render_dashboard

# Application Configuration
st.set_page_config(
    page_title="GlucoTwin | Clinical Digital Twin",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded",
)

# Inject Custom High-Contrast CSS Theme
inject_custom_css()

# Load Data and Model Artifacts
try:
    artifact = load_model()
    ehr = load_ehr()
    sensor = load_sensor()
    metrics = load_metrics()
except Exception as exc:
    st.error(f"Critical System Error: Unable to load data artifacts: {exc}")
    st.stop()

model = artifact["model"]
features = artifact["features"]

# Session State for View Navigation
# Session State for View Navigation
NAV_LANDING = "Executive Landing Page"
NAV_DASHBOARD = "Clinical Digital Twin OS"

if "nav_view" not in st.session_state:
    st.session_state.nav_view = NAV_LANDING

# Sidebar Navigation Toggle
with st.sidebar:
    st.markdown("### Navigation")
    st.radio(
        "Select Application View",
        [NAV_LANDING, NAV_DASHBOARD],
        key="nav_view",
        label_visibility="collapsed",
    )
    st.divider()

# Route to Selected View
if st.session_state.nav_view == NAV_LANDING:
    render_landing_page(metrics)
else:
    # Sidebar Controls for Patient Selection & Telemetry Stream
    with st.sidebar:
        st.markdown("### Patient Selection")
        patient_ids = ehr["patient_id"].tolist()
        patient_id = st.selectbox("Select Patient Profile", patient_ids, index=0)

        patient = ehr.loc[ehr["patient_id"] == patient_id].iloc[0]
        records = sensor.loc[sensor["patient_id"] == patient_id].copy()
        records = records.sort_values("timestamp").reset_index(drop=True)

        bmi_val = float(patient["bmi"])
        bmi_class = get_bmi_classification(bmi_val)

        # High-contrast white text in dark blue badge
        st.markdown(
            f"""
            <div class="patient-sidebar-card" style="background-color: #0f172a !important; background: #0f172a !important; padding: 14px 16px; border-radius: 8px; border: 1px solid #334155; margin-bottom: 14px;">
                <div style="font-weight: 800; color: #ffffff !important; -webkit-text-fill-color: #ffffff !important; font-size: 15px; margin-bottom: 5px;">{patient_id} ({patient['sex']}, {int(patient['age'])}y)</div>
                <div style="color: #ffffff !important; -webkit-text-fill-color: #ffffff !important; font-size: 12.5px; margin-bottom: 4px;">
                    HbA1c: <strong style="color: #ffffff !important; -webkit-text-fill-color: #ffffff !important;">{patient['hba1c']:.1f}%</strong> | 
                    BMI: <strong style="color: #ffffff !important; -webkit-text-fill-color: #ffffff !important;">{bmi_val:.1f}</strong> ({bmi_class})
                </div>
                <div style="color: #ffffff !important; -webkit-text-fill-color: #ffffff !important; font-size: 12.5px;">
                    T2D Duration: <strong style="color: #ffffff !important; -webkit-text-fill-color: #ffffff !important;">{patient['years_since_diagnosis']:.1f} yrs</strong>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.divider()

        st.markdown("### Sensor Telemetry Stream")
        st.caption("Controls live stream replay along continuous 5-minute intervals.")

        slider_key = f"sim_slider_{patient_id}"
        default_idx = max(24, len(records) - 24)
        if slider_key not in st.session_state:
            st.session_state[slider_key] = default_idx

        def set_idx(val):
            st.session_state[slider_key] = max(24, min(val, len(records) - 1))

        c_b1, c_b2 = st.columns(2)
        with c_b1:
            st.button(
                "[-5 min]",
                use_container_width=True,
                disabled=(st.session_state[slider_key] <= 24),
                on_click=set_idx,
                args=(st.session_state[slider_key] - 1,),
            )
        with c_b2:
            st.button(
                "[+5 min]",
                use_container_width=True,
                disabled=(st.session_state[slider_key] >= len(records) - 1),
                on_click=set_idx,
                args=(st.session_state[slider_key] + 1,),
            )

        c_b3, c_b4 = st.columns(2)
        with c_b3:
            st.button(
                "[Rewind 2h]",
                use_container_width=True,
                on_click=set_idx,
                args=(max(24, len(records) - 25),),
            )
        with c_b4:
            st.button(
                "[Latest]",
                use_container_width=True,
                on_click=set_idx,
                args=(len(records) - 1,),
            )

        idx = st.slider(
            "Timeline Scrubber",
            min_value=24,
            max_value=len(records) - 1,
            key=slider_key,
        )

        current_ts = records.iloc[idx]["timestamp"]
        st.caption(
            f"Timeline: Index {idx + 1} of {len(records)} | Timestamp: {current_ts.strftime('%Y-%m-%d %H:%M')}"
        )

        st.divider()
        st.markdown("### Compliance & Governance")
        st.caption(
            "DPDP Act & HIPAA Compliant Sandbox. All records and biosignals are synthetic physiological models generated for clinical research evaluation."
        )

    # Slice telemetry and render the 5-Tab Dashboard
    visible = records.iloc[: idx + 1].copy()
    render_dashboard(
        patient=patient,
        visible=visible,
        model=model,
        features=features,
        metrics=metrics,
        patient_id=patient_id,
        bmi_class=bmi_class,
        idx=idx,
    )

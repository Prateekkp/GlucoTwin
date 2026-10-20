"""Executive Landing Page view for Happiest Health Summit 2026."""

import streamlit as st


def render_landing_page(metrics: dict):
    """Render high-impact Executive Landing Page."""
    # Hero Section
    st.markdown(
        """
        <div class="clinical-header">
            <div style="font-size: 11px; text-transform: uppercase; letter-spacing: 1.5px; color: #38bdf8; font-weight: 700; margin-bottom: 6px;">
                Happiest Health Summit 2026 | Bengaluru | Digital Twin PoC Challenge
            </div>
            <h1 class="clinical-title" style="color: #ffffff !important; font-size: 32px !important;">GLUCOTWIN: CLINICAL DIGITAL TWIN</h1>
            <p class="clinical-subtitle" style="color: #ffffff !important; font-size: 15px !important; max-width: 950px;">
                A Multimodal Physiological Digital Twin for Indian Type 2 Diabetes Cohorts. 
                Fusing longitudinal Electronic Health Records (EHR) with high-frequency wearable IoT telemetry to forecast adverse glycemic excursions 120 minutes in advance.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Launch CTA & Key Metrics Strip
    cta_col, m_col1, m_col2 = st.columns([1.6, 1.2, 1.2])
    with cta_col:
        st.write("**Experience the Clinical Platform:**")

        def _launch_dashboard():
            st.session_state.nav_view = "Clinical Digital Twin OS"

        st.button(
            "Launch Clinical Digital Twin OS",
            type="primary",
            use_container_width=True,
            on_click=_launch_dashboard,
        )

    with m_col1:
        st.metric("120-Min Forecast MAE", f"{metrics['model_mae_mg_dl']:.2f} mg/dL")
    with m_col2:
        baseline_mae = metrics["persistence_baseline_mae_mg_dl"]
        imp = 100.0 * (baseline_mae - metrics["model_mae_mg_dl"]) / baseline_mae
        st.metric("Error Reduction", f"{imp:.1f}% vs Baseline")

    st.divider()

    # Problem Statement Section (Indian Context)
    st.markdown("### The Healthcare Challenge in India: Why Digital Twins?")
    st.write(
        "India is home to over **101 million individuals living with Type 2 Diabetes** (ICMR-INDIAB study). Conventional diabetes management is overwhelmingly reactive, observing damage only after acute glycemic events occur."
    )

    p1, p2, p3 = st.columns(3)
    with p1:
        st.markdown(
            """
            <div class="feature-card">
                <h3>The South Asian Phenotype</h3>
                <p>
                    Asian Indians exhibit the "thin-fat" phenotype: higher visceral adiposity and pronounced insulin resistance at lower BMI cutoffs (ICMR defines Overweight at BMI >= 23 and Obese at >= 25 kg/m2).
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with p2:
        st.markdown(
            """
            <div class="feature-card">
                <h3>Carbohydrate Spike Dynamics</h3>
                <p>
                    Traditional diets rich in refined carbohydrates (rotis, white rice) induce rapid post-prandial glycemic excursions that standard finger-prick checks miss until cellular distress has already occurred.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with p3:
        st.markdown(
            """
            <div class="feature-card">
                <h3>Reactive vs Proactive Care</h3>
                <p>
                    Retrospective HbA1c testing every 90 days provides an aggregated look back, but cannot prevent acute nocturnal hypoglycemia (<70 mg/dL) or post-meal hyperglycemia spikes (>180 mg/dL).
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("### Core Digital Twin Capabilities")
    f1, f2, f3 = st.columns(3)

    with f1:
        st.markdown(
            """
            <div class="feature-card">
                <h3>1. Dual-Stream Fusion Engine</h3>
                <p>
                    Merges static clinical history (age, BMI, HbA1c, disease duration, active pharmacotherapy) with dynamic 5-minute IoT biosignals (CGM glucose, wearable heart rate, step accumulation, sleep stages).
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with f2:
        st.markdown(
            """
            <div class="feature-card">
                <h3>2. 120-Min Early Warning System</h3>
                <p>
                    Projects glycemic trajectory 2 hours into the future, providing clinical action alerts and physiological explainability (rate of change, stress-induced hepatic output, diurnal dawn kinetics).
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with f3:
        st.markdown(
            """
            <div class="feature-card">
                <h3>3. Counterfactual 'What-If' Sandbox</h3>
                <p>
                    Allows physicians to simulate candidate interventions (15-min post-meal walk, insulin correction dose, low-glycemic dietary substitute) in a virtual replica before clinical prescription.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.divider()

    # System Architecture Schematic
    st.markdown("### Technical Architecture & Data Ingestion Pipeline")
    st.markdown(
        """
        ```
        +-----------------------------------------------------------------------------------+
        |                           DUAL-STREAM DATA INGESTION                              |
        |  [Static EHR Profile]                      [Dynamic Wearable Stream]              |
        |  - Demographics (Age, Sex, BMI)            - 5-Min Interstitial CGM Glucose       |
        |  - T2D Duration & Comorbidities (HTN, CKD) - Wearable Heart Rate (BPM)            |
        |  - Pharmacotherapy (Metformin, SGLT2i, etc)- Physical Activity (5-min Steps)     |
        |  - Baseline Glycated Hemoglobin (HbA1c)    - Circadian Sleep-Wake Phase           |
        +-------------------------------------+---------------------------------------------+
                                              |
                                              v
        +-----------------------------------------------------------------------------------+
        |                            FEATURE FUSION ENGINE                                  |
        |  - Multi-Scale Temporal Lags: Glucose Lags at 15m, 30m, 60m, 120m (Lags 3,6,12,24)|
        |  - Rolling Kinetics: 30-min & 60-min Rolling Means, 30-min Glucose Velocity       |
        |  - Physiological Sympathetic Drive: 30-min Mean Heart Rate Dynamics               |
        |  - Circadian Phase Encoding: Sin/Cos 24-hour Diurnal Harmonic Decomposition       |
        +-------------------------------------+---------------------------------------------+
                                              |
                                              v
        +-----------------------------------------------------------------------------------+
        |                    PREDICTIVE MODEL (RANDOM FOREST REGRESSOR)                     |
        |  - 26 Cross-Modal Fused Features | Horizon: T + 120 Minutes                       |
        |  - GroupShuffleSplit Validation: Tested strictly on held-out unseen patient twins |
        |  - Performance: 11.44 mg/dL MAE (39.9% error reduction over persistence baseline) |
        +-------------------------------------+---------------------------------------------+
                                              |
                                              v
        +-----------------------------------------------------------------------------------+
        |                      CLINICAL OS & DECISION SUPPORT SUITE                         |
        |  [Ambulatory Glucose Profile] [120-Min Adverse Alert] [What-If Twin Intervention] |
        +-----------------------------------------------------------------------------------+
        ```
        """
    )

    st.divider()

    # Team & Institutional Affiliation
    st.markdown("### Team & Institutional Affiliation")
    t1, t2 = st.columns([1, 2])
    with t1:
        st.markdown(
            """
            <div class="feature-card">
                <h3>Institution</h3>
                <p>
                    <strong>K.R. Mangalam University</strong><br>
                    School of Engineering & Technology<br>
                    B.Tech CSE (Data Science), 4th Year
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with t2:
        st.markdown(
            """
            <div class="feature-card">
                <h3>Team Members</h3>
                <p>
                    1. <strong>Prateek Kumar Prasad</strong> (Team Leader) — B.Tech CSE (DS), 4th Year<br>
                    2. <strong>Akshat Sharma</strong> — B.Tech CSE (DS), 4th Year<br>
                    3. <strong>Yatharth Chopra</strong> — B.Tech CSE (DS), 4th Year
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.divider()

    # Footer & Governance
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        st.markdown(
            """
            **Governance & DPDP Act 2023 Compliance:**
            All clinical profiles and biosignals are generated in a certified synthetic research sandbox. Calibrated to empirical clinical equations (Nathan et al. ADAG formula, ICMR-India BMI cutoffs) without ingesting real Protected Health Information (PHI).
            """
        )
    with col_f2:
        st.markdown(
            """
            **Happiest Health Summit 2026 Submission:**
            Track: Chronic Condition Digital Twin (Type 2 Diabetes)  
            Institution: K.R. Mangalam University  
            Codebase & Models: Licensed under the MIT Open Source License.
            """
        )

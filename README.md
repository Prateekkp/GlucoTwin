# GlucoTwin: Clinical Patient Digital Twin Platform

### Predictive Glycemic Management & Adverse Event Early Warning System
**Happiest Health Reimagining and Reforming Healthcare in India Summit 2026 (Bengaluru)**  
*Proof-of-Concept (PoC) Challenge — Track: Chronic Condition Digital Twin (Type 2 Diabetes)*

* **Live Deployed Application**: [GlucoTwin | Clinical Digital Twin (Streamlit Cloud)](https://gluco-twin.streamlit.app/)
* **Demonstration Video**: [GlucoTwin Comprehensive Demo Video (Google Drive)](https://drive.google.com/file/d/170j2lHUn91Lq56DxBENEc6oDBabGSrWg/view?usp=sharing)

---

## Submission Checklist Compliance

| Checklist Item | Status | Section Reference |
| :--- | :---: | :--- |
| **Team Details** | Verified | [Section 1: Team Details](#1-team-details) |
| **College / Incubator Information** | Verified | [Section 2: College and Institutional Information](#2-college-and-institutional-information) |
| **Project Title** | Verified | [Section 3: Project Title](#3-project-title) |
| **Problem Statement** | Verified | [Section 4: Problem Statement](#4-problem-statement) |
| **Healthcare Use Case** | Verified | [Section 5: Healthcare Use Case (Indian Cohorts)](#5-healthcare-use-case-indian-cohorts) |
| **Technical Stack** | Verified | [Section 6: Technical Stack](#6-technical-stack) |
| **AI/ML Model or Framework Details** | Verified | [Section 7: AI/ML Model and Framework Details](#7-aiml-model-and-framework-details) |
| **15-20 minute Demo Video (Unlisted YouTube)** | Verified | [Section 8: Demonstration Video Link](#8-15-20-minute-demo-video-unlisted-youtube) |
| **Open-source License Details** | Verified | [Section 9: Open-Source License Details](#9-open-source-license-details) |
| **Architecture Diagram in PDF/PPT format** | Verified | [Section 10: Architecture Diagram (PDF/PPT)](#10-architecture-diagram-in-pdfppt-format) |
| **Presentation in PDF/PPT format** | Verified | [Section 11: Presentation Deck (PDF/PPT)](#11-presentation-in-pdfppt-format-covering-project-details-and-outcomes) |
| **Public Accessibility of All Files & Links** | Verified | [Section 12: Public Accessibility Statement](#12-public-accessibility-of-files-and-links) |

---

## 1. Team Details
* **Team Members**:
  1. **Prateek Kumar Prasad** (Team Leader) — B.Tech CSE (Data Science), 4th Year
  2. **Akshat Sharma** — B.Tech CSE (Data Science), 4th Year
  3. **Yatharth Chopra** — B.Tech CSE (Data Science), 4th Year

---

## 2. College and Institutional Information
* **College / University**: K.R. Mangalam University
* **School**: School of Engineering & Technology
* **Department**: Department of Computer Science & Engineering (Data Science)
* **Location**: Gurugram, Haryana, India
* **Incubator / Lab Affiliation**: Center of Excellence in Artificial Intelligence & Healthcare Analytics, K.R. Mangalam University

---

## 3. Project Title
**GlucoTwin: A Dual-Stream Multimodal Digital Twin for 120-Minute Proactive Glycemic Event Forecasting and Counterfactual Physician Decision Support in Indian Type 2 Diabetes Cohorts**

---

## 4. Problem Statement
India is the diabetes capital of the world, with over **101 million individuals diagnosed with Type 2 Diabetes** (ICMR-INDIAB national survey). Standard diabetes care is overwhelmingly **reactive**:
- Patients rely on retrospective finger-pricks or quarterly HbA1c lab checks (every 90 days), detecting glycemic failure only after acute cellular damage has taken place.
- Acute glucose excursions—specifically sudden post-prandial hyperglycemia spikes (>180 mg/dL) and dangerous nocturnal hypoglycemia crashes (<70 mg/dL)—frequently occur unmonitored between clinical appointments, resulting in microvascular complications (neuropathy, retinopathy) and cardiovascular stress.

---

## 5. Healthcare Use Case (Indian Cohorts)
GlucoTwin specifically models the localized pathophysiological nuances of the **Asian Indian Phenotype**:
- **The "Thin-Fat" Phenotype**: Indians manifest elevated visceral adiposity, hyperinsulinemia, and premature beta-cell exhaustion at lower Body Mass Index levels. As recognized by the Indian Council of Medical Research (ICMR), overweight is classified at **BMI $\ge 23$ kg/m²** and obesity at **BMI $\ge 25$ kg/m²** (contrasting Western cutoffs of 25 and 30).
- **High-Glycemic Carbohydrate Excursions**: Traditional Indian diets heavily reliant on polished white rice and refined wheat rotis trigger rapid post-meal glucose spikes.
- **The Digital Twin Solution**: GlucoTwin synthesizes static EHR demographics with continuous 5-minute IoT wearable telemetry to project blood glucose **120 minutes into the future**. It enables doctors to test **counterfactual "What-If" interventions** (e.g., immediate 15-minute post-prandial walk vs. correction insulin vs. dietary carbohydrate reduction) in a virtual sandbox before clinical prescription.

---

## 6. Technical Stack
* **Language & Runtime**: Python 3.10+
* **Frontend / Clinical OS Interface**: Streamlit (Modular component architecture)
* **Data Manipulation & Time-Series**: `pandas`, `numpy`
* **Machine Learning & Preprocessing**: `scikit-learn`
* **Interactive Clinical Visualizations**: `Plotly` & Plotly Subplots (Synchronized multi-tier time-series)
* **Model Serialization**: `joblib`

---

## 7. AI/ML Model and Framework Details
* **Model Algorithm**: Random Forest Regressor ensemble (`n_estimators=100`, `max_depth=16`, `min_samples_leaf=5`, `random_state=42`)
* **Dual-Stream Feature Fusion (26 Features)**:
  - *Static Clinical Stream (EHR)*: Age, Sex, BMI, Years since T2D diagnosis, Baseline HbA1c, Hypertension flag, CKD flag, Active medications (Metformin, SGLT2i, Sulfonylurea, Basal/Bolus Insulin).
  - *Dynamic Wearable Telemetry Stream (IoT)*: Current CGM glucose, multi-scale temporal lags (Lags at 15m, 30m, 60m, 120m), rolling kinetic means (30m & 60m windows), short-term glucose velocity (30m delta), sympathetic stress heart rate (30m mean BPM), physical step counts (5m & 30m sum), sleep-wake state, and 24-hour diurnal circadian harmonic decomposition (`hour_sin`, `hour_cos`).
* **Validation Methodology**: Strict **GroupShuffleSplit (80% train / 20% test grouped by patient ID)**, evaluating strictly on 24 held-out patients never seen during training:

| Metric | Random Forest Digital Twin | Persistence Baseline | Clinical Significance |
| :--- | :--- | :--- | :--- |
| **Mean Absolute Error (MAE)** | **11.44 mg/dL** | 19.05 mg/dL | **39.9% error reduction** |
| **Root Mean Squared Error (RMSE)** | **15.16 mg/dL** | 24.82 mg/dL | Suppresses extreme spike prediction errors |
| **R² Score** | **0.8298** | 0.6120 | Explains ~83% of variance across cohorts |
| **Validation Cohort** | 24 held-out synthetic patients | 94,782 time-series rows | Zero patient overlap between train/test |

*Clinical Targets (RSSDI / International Consensus on Time in Range)*:
- Time In Range (TIR, 70–180 mg/dL): Target >70%
- Time Above Range (TAR, >180 mg/dL): Target <25%
- Time Below Range (TBR, <70 mg/dL): Target <4%
- Glycemic Variability (CV%): Target $\le 36\%$

---

## 8. 15-20 Minute Demo Video (Unlisted YouTube / Drive)
* **Demo Video Link**: [GlucoTwin Comprehensive Demonstration Video](https://drive.google.com/file/d/170j2lHUn91Lq56DxBENEc6oDBabGSrWg/view?usp=sharing)
*(The full comprehensive walk-through demonstrating the prototype, clinical workflow, dual-stream data fusion architecture, and "What-If" simulator is accessible via the link above).*

---

## 9. Open-Source License Details
This project is licensed under the **MIT License**. Full license terms are available in the [LICENSE](LICENSE) file in this repository.

---

## 10. Architecture Diagram in PDF/PPT Format
* **PDF Format**: [`docs/Architecture-Diagram-GlucoTwin.pdf`](docs/Architecture-Diagram-GlucoTwin.pdf)
* **Direct Repository Link**: [Architecture-Diagram-GlucoTwin.pdf](docs/Architecture-Diagram-GlucoTwin.pdf)
* *Summary Pipeline*:
```
[Stream 1: Static EHR] + [Stream 2: Dynamic Wearables]
                       |
                       v
         [Multi-Scale Lag & Feature Engine]
                       |
                       v
        [Random Forest 120-Min Inference]
                       |
                       v
   [Clinical OS Dashboard & What-If Sandbox]
```

---

## 11. Presentation in PDF/PPT Format Covering Project Details and Outcomes
* **Presentation Format**: [`docs/GlucoTwin_Presentation.pptx`](docs/GlucoTwin_Presentation.pptx)
* **Direct Repository Link**: [GlucoTwin_Presentation.pptx](docs/GlucoTwin_Presentation.pptx)
* *Deck Structure*:
  1. Title, Team & Institutional Details (K.R. Mangalam University)
  2. The Crisis: Type 2 Diabetes & the Indian "Thin-Fat" Phenotype
  3. Digital Twin Concept & Dual-Stream Architecture
  4. Data Pipeline & Feature Engineering
  5. Machine Learning Validation & Results vs. Persistence Baseline
  6. Clinical Decision Support & "What-If" Counterfactual Simulation
  7. DPDP Act 2023 Compliance & Synthetic Sandbox Rules
  8. Future Roadmap & Real-World Clinical Integration

---

## 12. Public Accessibility of Files and Links
* **Live Deployed Web Application**: [GlucoTwin Streamlit Cloud Deployment](https://gluco-twin.streamlit.app/) (Instant cloud access with zero local setup required).
* **Repository Visibility**: This repository is **100% public** and accessible without requiring credentials or additional permissions.
* **Open Source**: All source code, data generators, models, and documentation are directly cloned and executable under the MIT License.
* **Privacy Compliance**: Operates in a certified synthetic sandbox conforming to India's **Digital Personal Data Protection (DPDP) Act 2023** and global HIPAA guidelines, containing zero Protected Health Information (PHI).

---

## 13. Repository Structure
```
GlucoTwin/
├── app.py                   # Clean Streamlit orchestration entrypoint (<150 lines)
├── requirements.txt         # Project dependencies
├── LICENSE                  # MIT Open Source License
├── README.md                # Submission documentation
├── src/                     # Modular production package
│   ├── __init__.py
│   ├── generate_data.py     # Synthetic EHR & CGM/wearable time-series generator
│   ├── train.py             # Multi-stream feature fusion & model training
│   ├── config.py            # Paths, clinical constants & ICMR thresholds
│   ├── styles.py            # Custom high-contrast CSS theme injection
│   ├── data_loader.py       # Cached model and dataset loaders
│   ├── features.py          # Feature extraction & counterfactual transforms
│   ├── charts.py            # Synchronized 3-tier Plotly visualization builders
│   └── views/
│       ├── __init__.py
│       ├── landing_page.py  # Executive Summit Landing Page view
│       └── dashboard.py     # 5-Tab Clinical Digital Twin OS dashboard
├── models/
│   ├── glucose_model.joblib # Serialized model artifact
│   ├── metrics.json         # Evaluated validation metrics
│   └── result.txt           # Benchmark audit logs
├── data/
│   ├── ehr.csv              # Synthetic EHR clinical profiles
│   └── sensor_readings.csv  # 5-minute time-series wearable readings
└── docs/
    ├── README.md                          # Docs directory guide & resources
    ├── Architecture-Diagram-GlucoTwin.pdf # System architecture diagram (PDF)
    └── GlucoTwin_Presentation.pptx        # Project pitch presentation (PPTX)
```

---

## 14. Quickstart: Running Locally

```bash
# 1. Clone repository
git clone https://github.com/[your-username]/GlucoTwin.git
cd GlucoTwin

# 2. Virtual environment setup
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

# 3. Install requirements
pip install -r requirements.txt

# 4. Generate data & train model
python src/generate_data.py
python src/train.py

# 5. Launch interactive clinical dashboard
streamlit run app.py
```
Open browser at `http://localhost:8501`.

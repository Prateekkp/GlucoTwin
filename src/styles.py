"""Clinical OS custom styles and CSS injection."""

import streamlit as st


def inject_custom_css():
    """Inject high-contrast, professional clinical dashboard styles."""
    st.markdown(
        """
        <style>
        /* Global layout & typography */
        .block-container {
            padding-top: 4.5rem !important;
            padding-bottom: 2.5rem !important;
        }
        
        /* Header card */
        .clinical-header {
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%) !important;
            border: 1px solid #334155 !important;
            border-radius: 8px !important;
            padding: 22px 26px !important;
            margin-top: 8px !important;
            margin-bottom: 20px !important;
        }
        .clinical-header h1,
        .clinical-header .clinical-title,
        h1.clinical-title,
        .clinical-title {
            color: #ffffff !important;
            font-size: 26px !important;
            font-weight: 800 !important;
            letter-spacing: -0.5px !important;
            margin: 0 !important;
            line-height: 1.2 !important;
        }
        .clinical-header p,
        .clinical-header .clinical-subtitle,
        p.clinical-subtitle,
        .clinical-subtitle {
            color: #ffffff !important;
            font-size: 13.5px !important;
            margin-top: 6px !important;
            margin-bottom: 0 !important;
            line-height: 1.5 !important;
        }
        
        /* Metric and status chips */
        .chip {
            display: inline-block;
            padding: 3px 10px;
            border-radius: 4px;
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-right: 6px;
        }
        .chip-blue { background: #0369a1; color: #ffffff !important; }
        .chip-green { background: #065f46; color: #ffffff !important; }
        .chip-amber { background: #92400e; color: #ffffff !important; }
        .chip-red { background: #991b1b; color: #ffffff !important; }
        .chip-slate { background: #334155; color: #ffffff !important; }
        
        /* Card containers */
        .clinical-card {
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%) !important;
            border: 1px solid #334155 !important;
            border-radius: 6px !important;
            padding: 12px 18px !important;
            margin-bottom: 14px !important;
            color: #ffffff !important;
        }
        .clinical-card * {
            color: #ffffff !important;
        }
        .clinical-card-header {
            font-size: 13px !important;
            font-weight: 700 !important;
            color: #ffffff !important;
            text-transform: uppercase !important;
            letter-spacing: 0.5px !important;
            margin-bottom: 0 !important;
            border-bottom: none !important;
            padding-bottom: 0 !important;
        }
        
        /* Sidebar Patient Card High-Contrast Styling */
        section[data-testid="stSidebar"] .patient-sidebar-card,
        .patient-sidebar-card {
            background-color: #0f172a !important;
            background: #0f172a !important;
            border: 1px solid #334155 !important;
            border-radius: 8px !important;
            padding: 14px 16px !important;
            margin-bottom: 14px !important;
        }
        
        section[data-testid="stSidebar"] .patient-sidebar-card,
        section[data-testid="stSidebar"] .patient-sidebar-card div,
        section[data-testid="stSidebar"] .patient-sidebar-card span,
        section[data-testid="stSidebar"] .patient-sidebar-card strong,
        section[data-testid="stSidebar"] .patient-sidebar-card p,
        .patient-sidebar-card,
        .patient-sidebar-card * {
            color: #ffffff !important;
            -webkit-text-fill-color: #ffffff !important;
        }
        
        /* Landing page feature cards */
        .feature-card {
            background: #1e293b;
            border: 1px solid #334155;
            border-radius: 8px;
            padding: 20px;
            height: 100%;
            margin-bottom: 16px;
        }
        .feature-card h3 {
            color: #38bdf8 !important;
            font-size: 16px !important;
            font-weight: 700 !important;
            margin-top: 0 !important;
            margin-bottom: 8px !important;
        }
        .feature-card p {
            color: #cbd5e1 !important;
            font-size: 13px !important;
            line-height: 1.5 !important;
            margin-bottom: 0 !important;
        }

        /* Prevent tooltips from sticking on click */
        div[data-baseweb="tooltip"],
        div[data-baseweb="popover"],
        .stTooltipContent {
            pointer-events: none !important;
        }
        
        /* Risk alert banners */
        .alert-high {
            background-color: #450a0a;
            border-left: 4px solid #ef4444;
            color: #fecaca;
            padding: 12px 16px;
            border-radius: 4px;
            margin-bottom: 16px;
            font-size: 13px;
        }
        .alert-low {
            background-color: #451a03;
            border-left: 4px solid #f59e0b;
            color: #fed7aa;
            padding: 12px 16px;
            border-radius: 4px;
            margin-bottom: 16px;
            font-size: 13px;
        }
        .alert-normal {
            background-color: #064e3b;
            border-left: 4px solid #10b981;
            color: #a7f3d0;
            padding: 12px 16px;
            border-radius: 4px;
            margin-bottom: 16px;
            font-size: 13px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

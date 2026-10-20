"""Clinical charting and interactive visualization components."""

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from src.config import HIGH_GLUCOSE_THRESHOLD, LOW_GLUCOSE_THRESHOLD


def create_ambulatory_glucose_chart(
    history_window: pd.DataFrame,
    current_timestamp: pd.Timestamp,
    current_glucose: float,
    forecast_timestamp: pd.Timestamp,
    prediction: float,
) -> go.Figure:
    """Build a 3-tier synchronized clinical time-series figure with clean spacing and white text."""
    fig = make_subplots(
        rows=3,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.08,
        row_heights=[0.60, 0.20, 0.20],
        subplot_titles=[
            "Continuous Interstitial Glucose Stream & 120-Minute Digital Twin Forecast",
            "Wearable Heart Rate (BPM)",
            "Physical Activity (Steps per 5-min Interval)",
        ],
    )

    # 1. Glucose trajectory
    fig.add_trace(
        go.Scatter(
            x=history_window["timestamp"],
            y=history_window["glucose_mgdl"],
            name="Observed Glucose",
            mode="lines",
            line=dict(color="#38bdf8", width=2.5),
        ),
        row=1,
        col=1,
    )

    # Shaded Target Zone (70 to 180 mg/dL)
    fig.add_hrect(
        y0=LOW_GLUCOSE_THRESHOLD,
        y1=HIGH_GLUCOSE_THRESHOLD,
        fillcolor="rgba(16, 185, 129, 0.12)",
        line_width=0,
        annotation_text="Target Range (70-180 mg/dL)",
        annotation_position="top left",
        annotation_font=dict(color="#34d399", size=11),
        row=1,
        col=1,
    )

    # Threshold lines
    fig.add_hline(
        y=HIGH_GLUCOSE_THRESHOLD,
        line=dict(color="#ef4444", dash="dot", width=1.5),
        annotation_text="Hyperglycemia (180)",
        annotation_position="top right",
        annotation_font=dict(color="#f87171", size=11),
        row=1,
        col=1,
    )
    fig.add_hline(
        y=LOW_GLUCOSE_THRESHOLD,
        line=dict(color="#f59e0b", dash="dot", width=1.5),
        annotation_text="Hypoglycemia (70)",
        annotation_position="bottom right",
        annotation_font=dict(color="#fbbf24", size=11),
        row=1,
        col=1,
    )

    # 120-Minute Forecast Vector
    fig.add_trace(
        go.Scatter(
            x=[current_timestamp, forecast_timestamp],
            y=[current_glucose, prediction],
            name="120-Min Twin Forecast",
            mode="lines+markers",
            line=dict(color="#f43f5e", width=3, dash="dash"),
            marker=dict(size=8, color="#f43f5e"),
        ),
        row=1,
        col=1,
    )

    # 2. Wearable Heart Rate
    fig.add_trace(
        go.Scatter(
            x=history_window["timestamp"],
            y=history_window["heart_rate_bpm"],
            name="Heart Rate",
            mode="lines",
            line=dict(color="#ec4899", width=1.5),
        ),
        row=2,
        col=1,
    )

    # 3. Steps / Physical Activity
    fig.add_trace(
        go.Bar(
            x=history_window["timestamp"],
            y=history_window["steps"],
            name="Step Count",
            marker_color="#10b981",
        ),
        row=3,
        col=1,
    )

    # Layout configuration with generous top margin and pure white text
    fig.update_layout(
        height=660,
        margin=dict(l=45, r=40, t=95, b=35),
        hovermode="x unified",
        legend=dict(
            orientation="h",
            y=1.14,
            x=0.0,
            xanchor="left",
            yanchor="bottom",
            font=dict(color="#ffffff", size=12),
            bgcolor="rgba(15, 23, 42, 0.85)",
            bordercolor="#334155",
            borderwidth=1,
        ),
        plot_bgcolor="#0f172a",
        paper_bgcolor="#0f172a",
        font=dict(color="#ffffff", size=11),
    )

    # Ensure all subplot title annotations are crisp white and positioned properly
    for ann in fig.layout.annotations:
        ann.font.color = "#ffffff"
        ann.font.size = 12.5

    fig.update_yaxes(
        title_text="Glucose (mg/dL)",
        title_font=dict(color="#ffffff"),
        tickfont=dict(color="#cbd5e1"),
        row=1,
        col=1,
        gridcolor="#334155",
    )
    fig.update_yaxes(
        title_text="BPM",
        title_font=dict(color="#ffffff"),
        tickfont=dict(color="#cbd5e1"),
        row=2,
        col=1,
        gridcolor="#334155",
    )
    fig.update_yaxes(
        title_text="Steps",
        title_font=dict(color="#ffffff"),
        tickfont=dict(color="#cbd5e1"),
        row=3,
        col=1,
        gridcolor="#334155",
    )
    fig.update_xaxes(
        tickfont=dict(color="#cbd5e1"),
        gridcolor="#334155",
    )

    return fig


def create_counterfactual_chart(
    history_window: pd.DataFrame,
    current_timestamp: pd.Timestamp,
    current_glucose: float,
    forecast_timestamp: pd.Timestamp,
    baseline_prediction: float,
    counterfactual_prediction: float,
) -> go.Figure:
    """Build comparative trajectory figure for physician What-If simulations."""
    fig = go.Figure()

    # Historical observed line (last 36 points = 3 hours)
    recent_history = history_window.tail(36)
    fig.add_trace(
        go.Scatter(
            x=recent_history["timestamp"],
            y=recent_history["glucose_mgdl"],
            name="Observed History",
            mode="lines",
            line=dict(color="#64748b", width=2),
        )
    )

    # Baseline trajectory (no intervention)
    fig.add_trace(
        go.Scatter(
            x=[current_timestamp, forecast_timestamp],
            y=[current_glucose, baseline_prediction],
            name="Baseline Trajectory (No Action)",
            mode="lines+markers",
            line=dict(color="#ef4444", width=3, dash="dash"),
            marker=dict(size=8, color="#ef4444"),
        )
    )

    # Counterfactual simulated trajectory
    fig.add_trace(
        go.Scatter(
            x=[current_timestamp, forecast_timestamp],
            y=[current_glucose, counterfactual_prediction],
            name="Counterfactual Twin (With Intervention)",
            mode="lines+markers",
            line=dict(color="#10b981", width=3, dash="solid"),
            marker=dict(size=9, color="#10b981"),
        )
    )

    fig.add_hrect(
        y0=LOW_GLUCOSE_THRESHOLD,
        y1=HIGH_GLUCOSE_THRESHOLD,
        fillcolor="rgba(16, 185, 129, 0.08)",
        line_width=0,
        annotation_text="Target Corridor (70-180 mg/dL)",
        annotation_font=dict(color="#34d399", size=11),
    )

    fig.update_layout(
        title=dict(
            text="Digital Twin 'What-If' Simulation: Baseline vs Intervention Trajectory (Next 120 Minutes)",
            font=dict(color="#ffffff", size=13.5),
            x=0.01,
            y=0.98,
        ),
        height=420,
        margin=dict(l=45, r=40, t=75, b=35),
        xaxis_title="Time",
        yaxis_title="Glucose (mg/dL)",
        plot_bgcolor="#0f172a",
        paper_bgcolor="#0f172a",
        font=dict(color="#ffffff"),
        legend=dict(
            orientation="h",
            y=1.14,
            x=0.0,
            xanchor="left",
            yanchor="bottom",
            font=dict(color="#ffffff", size=12),
            bgcolor="rgba(15, 23, 42, 0.85)",
            bordercolor="#334155",
            borderwidth=1,
        ),
    )
    fig.update_xaxes(
        title_font=dict(color="#ffffff"),
        tickfont=dict(color="#cbd5e1"),
        gridcolor="#334155",
    )
    fig.update_yaxes(
        title_font=dict(color="#ffffff"),
        tickfont=dict(color="#cbd5e1"),
        gridcolor="#334155",
    )

    return fig

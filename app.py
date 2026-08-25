from pathlib import Path

import folium
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
from streamlit_folium import st_folium

from dashboard.components import (
    render_alert_card,
    render_metric_cards,
    render_risk_gauge,
)
from src.config import DATA_FILE, MODEL_FILE, PILOT_AREA
from src.data.load_data import load_dataset
from src.features.engineering import prepare_features
from src.model.explain import get_feature_importance
from src.model.predict import predict_dataframe, predict_single
from src.model.train import train_model
from src.risk.engine import (
    alert_level,
    alert_message,
    risk_level,
    risk_color,
)

st.set_page_config(
    page_title="NER Landslide AI",
    page_icon="🏔️",
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_data
def get_data():
    return load_dataset(DATA_FILE)


@st.cache_resource
def get_model():
    if not MODEL_FILE.exists():
        train_model()
    return MODEL_FILE


def initialize_application():
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    MODEL_FILE.parent.mkdir(parents=True, exist_ok=True)

    if not DATA_FILE.exists():
        from src.data.generate_demo_data import generate_demo_dataset

        generate_demo_dataset(DATA_FILE)

    if not MODEL_FILE.exists():
        train_model()


def create_risk_map(dataframe: pd.DataFrame, selected_zone: str | None = None):
    center_lat = dataframe["latitude"].mean()
    center_lon = dataframe["longitude"].mean()

    fmap = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=9,
        tiles="OpenStreetMap",
    )

    for _, row in dataframe.iterrows():
        selected = row["zone_id"] == selected_zone
        radius = 9 if selected else 6
        color = risk_color(row["risk_score"])

        popup_text = f"""
        <b>{row['zone_id']}</b><br>
        Risk score: {row['risk_score']:.1f}/100<br>
        Level: {row['risk_level']}<br>
        Rainfall 24h: {row['rainfall_24h']:.1f} mm<br>
        Soil moisture: {row['soil_moisture']:.2f}<br>
        Slope: {row['slope']:.1f}°<br>
        Elevation: {row['elevation']:.0f} m
        """

        folium.CircleMarker(
            location=[row["latitude"], row["longitude"]],
            radius=radius,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.8,
            popup=folium.Popup(popup_text, max_width=280),
            tooltip=f"{row['zone_id']} — {row['risk_level']}",
        ).add_to(fmap)

    return fmap


def show_overview(dataframe: pd.DataFrame):
    st.title("🏔️ NER Landslide AI")
    st.subheader("Early Warning & Risk Monitoring System")

    st.info(
        "Prototype decision-support system for Sikkim. "
        "The risk values are not official government warning thresholds."
    )

    total_zones = len(dataframe)
    high_risk = int((dataframe["risk_score"] >= 51).sum())
    critical = int((dataframe["risk_score"] >= 76).sum())
    warnings = int((dataframe["alert_level"].isin(["WARNING", "CRITICAL"])).sum())

    render_metric_cards(total_zones, high_risk, critical, warnings)

    left, right = st.columns(2)

    with left:
        st.markdown("### Risk distribution")
        risk_counts = (
            dataframe["risk_level"]
            .value_counts()
            .rename_axis("Risk level")
            .reset_index(name="Zones")
        )
        order = ["LOW", "MODERATE", "HIGH", "CRITICAL"]
        risk_counts["Risk level"] = pd.Categorical(
            risk_counts["Risk level"],
            categories=order,
            ordered=True,
        )
        risk_counts = risk_counts.sort_values("Risk level")

        fig = px.bar(
            risk_counts,
            x="Risk level",
            y="Zones",
            color="Risk level",
            color_discrete_map={
                "LOW": "#2ca02c",
                "MODERATE": "#f1c40f",
                "HIGH": "#e67e22",
                "CRITICAL": "#d62728",
            },
        )
        st.plotly_chart(fig, use_container_width=True)

    with right:
        st.markdown("### Average environmental conditions")
        averages = pd.DataFrame(
            {
                "Feature": [
                    "Rainfall 24h",
                    "Rainfall 3-day",
                    "Rainfall 7-day",
                    "Soil moisture",
                    "Slope",
                ],
                "Value": [
                    dataframe["rainfall_24h"].mean(),
                    dataframe["rainfall_3day"].mean(),
                    dataframe["rainfall_7day"].mean(),
                    dataframe["soil_moisture"].mean() * 100,
                    dataframe["slope"].mean(),
                ],
            }
        )

        fig = px.bar(
            averages,
            x="Feature",
            y="Value",
            color="Feature",
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("### Highest-risk zones")
    columns = [
        "zone_id",
        "risk_score",
        "risk_level",
        "alert_level",
        "rainfall_24h",
        "soil_moisture",
        "slope",
    ]
    st.dataframe(
        dataframe.sort_values("risk_score", ascending=False)[columns].head(10),
        use_container_width=True,
        hide_index=True,
    )


def show_map(dataframe: pd.DataFrame):
    st.title("🗺️ Interactive Risk Map")

    selected_zone = st.selectbox(
        "Select a zone to highlight",
        options=["None"] + sorted(dataframe["zone_id"].unique().tolist()),
    )

    selected_zone = None if selected_zone == "None" else selected_zone

    fmap = create_risk_map(dataframe, selected_zone)
    st_folium(fmap, width=None, height=650, returned_objects=[])


def show_zone_analysis(dataframe: pd.DataFrame):
    st.title("📍 Zone Analysis")

    selected_zone = st.selectbox(
        "Choose a zone",
        sorted(dataframe["zone_id"].unique().tolist()),
    )

    zone = dataframe[dataframe["zone_id"] == selected_zone].iloc[0]
    score = float(zone["risk_score"])

    left, right = st.columns([1, 1])

    with left:
        render_risk_gauge(score, zone["risk_level"])
        st.markdown(f"### {selected_zone}")
        st.write(f"Coordinates: {zone['latitude']:.4f}, {zone['longitude']:.4f}")
        st.write(f"Historical landslide events: {int(zone['historical_landslide'])}")

    with right:
        st.markdown("### Environmental features")
        feature_table = pd.DataFrame(
            {
                "Feature": [
                    "Rainfall — 24 hours",
                    "Rainfall — 3 days",
                    "Rainfall — 7 days",
                    "Soil moisture",
                    "Elevation",
                    "Slope",
                    "Land cover",
                ],
                "Value": [
                    f"{zone['rainfall_24h']:.1f} mm",
                    f"{zone['rainfall_3day']:.1f} mm",
                    f"{zone['rainfall_7day']:.1f} mm",
                    f"{zone['soil_moisture']:.2f}",
                    f"{zone['elevation']:.0f} m",
                    f"{zone['slope']:.1f}°",
                    zone["land_cover"],
                ],
            }
        )
        st.table(feature_table)

    st.markdown("### Main risk drivers")
    drivers = zone["risk_drivers"].split("|")

    for driver in drivers:
        st.write(f"• {driver}")

    if zone["alert_level"] != "NONE":
        render_alert_card(
            zone["alert_level"],
            score,
            selected_zone,
            alert_message(zone["alert_level"]),
        )


def show_alerts(dataframe: pd.DataFrame):
    st.title("🚨 Alerts")

    alerts = dataframe[dataframe["alert_level"] != "NONE"].copy()
    alerts = alerts.sort_values("risk_score", ascending=False)

    if alerts.empty:
        st.success("No active prototype alerts.")
        return

    for _, zone in alerts.iterrows():
        render_alert_card(
            zone["alert_level"],
            zone["risk_score"],
            zone["zone_id"],
            alert_message(zone["alert_level"]),
        )


def show_simulator(dataframe: pd.DataFrame):
    st.title("🌧️ Rainfall Scenario Simulator")

    selected_zone = st.selectbox(
        "Choose a zone to simulate",
        sorted(dataframe["zone_id"].unique().tolist()),
        key="sim_zone",
    )

    zone = dataframe[dataframe["zone_id"] == selected_zone].iloc[0]
    original_rainfall = float(zone["rainfall_24h"])

    st.metric("Current 24-hour rainfall", f"{original_rainfall:.1f} mm")

    increase = st.slider(
        "Additional simulated rainfall",
        min_value=0,
        max_value=300,
        value=50,
        step=10,
    )

    simulated = zone.copy()
    simulated["rainfall_24h"] = original_rainfall + increase
    simulated["rainfall_3day"] = float(zone["rainfall_3day"]) + increase
    simulated["rainfall_7day"] = float(zone["rainfall_7day"]) + increase

    result = predict_single(simulated)
    new_score = result["risk_score"]
    new_level = result["risk_level"]
    new_alert = result["alert_level"]

    col1, col2, col3 = st.columns(3)
    col1.metric("Simulated rainfall", f"{simulated['rainfall_24h']:.1f} mm")
    col2.metric("New risk score", f"{new_score:.1f}/100")
    col3.metric("New risk level", new_level)

    render_risk_gauge(new_score, new_level)

    if new_alert != "NONE":
        render_alert_card(
            new_alert,
            new_score,
            selected_zone,
            alert_message(new_alert),
        )
    else:
        st.success("No prototype alert is triggered at this rainfall level.")

    comparison = pd.DataFrame(
        {
            "Scenario": ["Current", "Simulated"],
            "Rainfall 24h": [original_rainfall, simulated["rainfall_24h"]],
            "Risk score": [zone["risk_score"], new_score],
        }
    )

    fig = px.bar(
        comparison,
        x="Scenario",
        y=["Rainfall 24h", "Risk score"],
        barmode="group",
        title="Current versus simulated scenario",
    )
    st.plotly_chart(fig, use_container_width=True)


def show_model_explanation():
    st.title("🔍 Model Explainability")

    importance = get_feature_importance(MODEL_FILE)

    st.write(
        "These values show the relative contribution of input features "
        "to the Random Forest model's decisions. They are not causal proof."
    )

    fig = px.bar(
        importance.sort_values("importance"),
        x="importance",
        y="feature",
        orientation="h",
        title="Random Forest feature importance",
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### Interpretation")
    st.write(
        "Rainfall, soil moisture and slope are expected to be important "
        "dynamic and terrain-related risk indicators. Actual importance "
        "must be reported from the trained dataset."
    )


def main():
    initialize_application()

    dataframe = get_data()
    dataframe = prepare_features(dataframe)
    dataframe = predict_dataframe(dataframe)

    st.sidebar.title("Navigation")
    page = st.sidebar.radio(
        "Open page",
        [
            "Overview",
            "Risk Map",
            "Zone Analysis",
            "Alerts",
            "Rainfall Simulator",
            "Model Explanation",
        ],
    )

    st.sidebar.markdown("---")
    st.sidebar.caption(f"Pilot area: {PILOT_AREA}")
    st.sidebar.caption("Prototype — not an official warning service")

    if page == "Overview":
        show_overview(dataframe)
    elif page == "Risk Map":
        show_map(dataframe)
    elif page == "Zone Analysis":
        show_zone_analysis(dataframe)
    elif page == "Alerts":
        show_alerts(dataframe)
    elif page == "Rainfall Simulator":
        show_simulator(dataframe)
    elif page == "Model Explanation":
        show_model_explanation()


if __name__ == "__main__":
    main()
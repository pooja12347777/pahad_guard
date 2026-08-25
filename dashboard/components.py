import streamlit as st


def render_metric_cards(
    active_zones: int,
    high_risk: int,
    critical: int,
    warnings: int,
):
    columns = st.columns(4)

    columns[0].metric("Active zones", active_zones)
    columns[1].metric("High risk", high_risk)
    columns[2].metric("Critical", critical)
    columns[3].metric("Warnings", warnings)


def render_risk_gauge(score: float, level: str):
    score = max(0, min(100, score))

    st.progress(score / 100)
    st.metric("AI risk score", f"{score:.1f}/100")
    st.subheader(f"Risk level: {level}")


def render_alert_card(
    level: str,
    score: float,
    zone_id: str,
    message: str,
):
    if level == "CRITICAL":
        st.error(
            f"🚨 CRITICAL ALERT\n\n"
            f"Zone: {zone_id}\n\n"
            f"Risk: {score:.1f}/100\n\n"
            f"{message}"
        )
    elif level == "WARNING":
        st.warning(
            f"⚠️ WARNING\n\n"
            f"Zone: {zone_id}\n\n"
            f"Risk: {score:.1f}/100\n\n"
            f"{message}"
        )
    else:
        st.info(
            f"👀 WATCH\n\n"
            f"Zone: {zone_id}\n\n"
            f"Risk: {score:.1f}/100\n\n"
            f"{message}"
        )
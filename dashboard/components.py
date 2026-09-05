import streamlit as st

from dashboard.theme import RISK_COLORS, risk_badge_html


def render_metric_cards(
    active_zones: int,
    high_risk: int,
    critical: int,
    warnings: int,
):
    tiles = [
        ("Active zones", active_zones, "#5B8C6E"),
        ("High risk", high_risk, "#DB7C3C"),
        ("Critical", critical, "#C84A3E"),
        ("Warnings", warnings, "#D9A441"),
    ]

    html = '<div class="pg-tile-row">'
    for label, value, accent in tiles:
        html += (
            f'<div class="pg-tile" style="--tile-accent:{accent}">'
            f'<div class="pg-tile-value">{value}</div>'
            f'<div class="pg-tile-label">{label}</div>'
            f"</div>"
        )
    html += "</div>"

    st.markdown(html, unsafe_allow_html=True)


def render_risk_gauge(score: float, level: str):
    score = max(0, min(100, score))
    color = RISK_COLORS.get(level.upper(), "#5B8C6E")

    st.markdown(
        f"""
        <div style="margin-bottom: 0.6rem;">
            <div style="display:flex; align-items:baseline; gap:0.6rem;">
                <span style="font-family:'IBM Plex Mono',monospace; font-size:2.1rem; color:{color};">
                    {score:.1f}
                </span>
                <span style="color:#93A398; font-size:0.95rem;">/ 100 AI risk score</span>
            </div>
            <div style="background:#171E1B; border:1px solid #2A332E; border-radius:3px; height:10px; margin-top:0.5rem;">
                <div style="background:{color}; width:{score}%; height:100%; border-radius:2px;"></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(f"**Risk level:** {risk_badge_html(level)}", unsafe_allow_html=True)


def render_alert_card(
    level: str,
    score: float,
    zone_id: str,
    message: str,
):
    color = RISK_COLORS.get(level.upper(), "#5B8C6E")
    icon = {"CRITICAL": "🚨", "WARNING": "⚠️", "WATCH": "👀"}.get(level.upper(), "👀")

    st.markdown(
        f"""
        <div style="background:#171E1B; border:1px solid #2A332E; border-left:3px solid {color};
                    border-radius:3px; padding:0.9rem 1.1rem; margin-bottom:0.8rem;">
            <div style="font-family:'Space Grotesk',sans-serif; font-weight:600; color:{color}; margin-bottom:0.3rem;">
                {icon} {level} — Zone {zone_id}
            </div>
            <div style="font-family:'IBM Plex Mono',monospace; font-size:0.85rem; color:#93A398; margin-bottom:0.4rem;">
                Risk score: {score:.1f}/100
            </div>
            <div style="color:#E9EEE9; font-size:0.92rem;">{message}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

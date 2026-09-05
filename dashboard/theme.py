import streamlit as st

# Risk-severity palette — the only color family besides the moss-green
# brand accent. Reused everywhere a risk level or alert level is shown,
# so the mapping stays consistent across the whole app.
RISK_COLORS = {
    "LOW": "#4C9A6A",
    "MODERATE": "#D9A441",
    "HIGH": "#DB7C3C",
    "CRITICAL": "#C84A3E",
    "WATCH": "#5B8C6E",
    "WARNING": "#D9A441",
}

ACCENT = "#5B8C6E"
BG = "#10151A"
PANEL = "#171E1B"
BORDER = "#2A332E"
TEXT = "#E9EEE9"
TEXT_MUTED = "#93A398"


def inject_theme() -> None:
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap');

        html, body, [class*="css"] {{
            font-family: 'Inter', sans-serif;
        }}

        h1, h2, h3, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {{
            font-family: 'Space Grotesk', sans-serif;
            font-weight: 600;
            letter-spacing: -0.01em;
        }}

        /* App header block */
        .pg-header {{
            border-bottom: 1px solid {BORDER};
            padding-bottom: 0.9rem;
            margin-bottom: 1.6rem;
        }}
        .pg-header h1 {{
            font-size: 1.9rem;
            margin-bottom: 0.15rem;
            color: {TEXT};
        }}
        .pg-header p {{
            color: {TEXT_MUTED};
            font-size: 0.95rem;
            margin: 0;
        }}

        /* Instrument tiles (replace default st.metric look) */
        .pg-tile-row {{
            display: flex;
            gap: 1rem;
            margin-bottom: 1.8rem;
            flex-wrap: wrap;
        }}
        .pg-tile {{
            flex: 1 1 180px;
            background: {PANEL};
            border: 1px solid {BORDER};
            border-top: 3px solid var(--tile-accent, {ACCENT});
            border-radius: 3px;
            padding: 0.9rem 1.1rem 0.8rem;
        }}
        .pg-tile-value {{
            font-family: 'IBM Plex Mono', monospace;
            font-size: 1.9rem;
            font-weight: 500;
            color: {TEXT};
            line-height: 1.1;
        }}
        .pg-tile-label {{
            color: {TEXT_MUTED};
            font-size: 0.85rem;
            margin-top: 0.3rem;
        }}

        /* Risk / alert badges */
        .pg-badge {{
            display: inline-block;
            padding: 0.12rem 0.55rem;
            border-radius: 2px;
            font-family: 'IBM Plex Mono', monospace;
            font-size: 0.78rem;
            font-weight: 500;
            color: #10151A;
        }}

        /* Custom data table */
        .pg-table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 0.9rem;
        }}
        .pg-table th {{
            text-align: left;
            color: {TEXT_MUTED};
            font-weight: 500;
            font-size: 0.82rem;
            padding: 0.5rem 0.8rem;
            border-bottom: 1px solid {BORDER};
        }}
        .pg-table td {{
            padding: 0.55rem 0.8rem;
            border-bottom: 1px solid {BORDER};
            color: {TEXT};
        }}
        .pg-table td.pg-mono {{
            font-family: 'IBM Plex Mono', monospace;
        }}
        .pg-table tr:hover td {{
            background: rgba(91, 140, 110, 0.06);
        }}

        /* Sidebar */
        section[data-testid="stSidebar"] {{
            border-right: 1px solid {BORDER};
        }}
        section[data-testid="stSidebar"] .pg-sidebar-meta {{
            font-family: 'IBM Plex Mono', monospace;
            font-size: 0.78rem;
            color: {TEXT_MUTED};
            line-height: 1.6;
        }}

        /* Buttons */
        .stButton > button {{
            border-radius: 3px;
            border: 1px solid {BORDER};
        }}
        .stButton > button[kind="primary"] {{
            background: {ACCENT};
            border: none;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def risk_badge_html(level: str) -> str:
    color = RISK_COLORS.get(level.upper(), TEXT_MUTED)
    return f'<span class="pg-badge" style="background:{color}">{level}</span>'

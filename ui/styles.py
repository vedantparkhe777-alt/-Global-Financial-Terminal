import pandas as pd
import streamlit as st

LIGHT_CSS = """
<style>
    :root {
        --background-color: #f8fafc;
        --secondary-background-color: #ffffff;
        --text-color: #0f172a;
        --primary-color: #2563eb;
    }
    html, body, [data-testid="stAppViewContainer"], .stApp {
        background-color: #f8fafc !important;
        color: #0f172a !important;
    }
    header[data-testid="stHeader"] {
        background-color: #f8fafc !important;
    }
    h1, h2, h3, h4, p, span, label, div {
        color: #0f172a;
    }
    h1, h2, h3 {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        font-weight: 700;
    }
    div[data-testid="stRadio"] > div {
        background-color: #ffffff !important;
        padding: 8px 12px;
        border-radius: 10px;
        border: 1px solid #cbd5e1 !important;
        box-shadow: 0 1px 3px rgba(15, 23, 42, 0.06);
    }
    div[data-testid="stRadio"] label,
    div[data-testid="stRadio"] label p,
    div[data-testid="stRadio"] span {
        color: #0f172a !important;
        font-weight: 600 !important;
        opacity: 1 !important;
    }
    div[data-testid="stExpander"] {
        background-color: #ffffff !important;
        border: 1px solid #cbd5e1 !important;
        border-radius: 10px !important;
    }
    div[data-testid="stExpander"] summary,
    div[data-testid="stExpander"] summary span,
    div[data-testid="stExpander"] summary p {
        background-color: #ffffff !important;
        color: #0f172a !important;
    }
    button[kind="secondary"], div[data-testid="stButton"] > button, a[data-testid="stBaseLinkButton-secondary"] {
        background-color: #ffffff !important;
        color: #0f172a !important;
        border: 1px solid #cbd5e1 !important;
        font-weight: 600 !important;
    }
    button[kind="secondary"]:hover, div[data-testid="stButton"] > button:hover {
        background-color: #eff6ff !important;
        border-color: #2563eb !important;
    }
    code {
        background-color: #e2e8f0 !important;
        color: #0f172a !important;
        border: 1px solid #cbd5e1 !important;
        padding: 2px 6px !important;
        border-radius: 5px !important;
        font-weight: 600 !important;
    }
    div[data-testid="stMetric"] {
        background: #ffffff !important;
        border: 1px solid #cbd5e1 !important;
        border-radius: 10px;
        padding: 14px 18px;
        box-shadow: 0 2px 6px rgba(15, 23, 42, 0.05);
    }
    div[data-testid="stMetricLabel"], div[data-testid="stMetricLabel"] p {
        color: #475569 !important;
        font-size: 0.85rem !important;
    }
    div[data-testid="stMetricValue"], div[data-testid="stMetricValue"] div {
        color: #0f172a !important;
        font-weight: 700 !important;
    }
    div[data-testid="stDataFrame"] {
        border: 1px solid #cbd5e1 !important;
        border-radius: 10px;
        overflow: hidden;
        background-color: #ffffff !important;
    }
    div[data-testid="stDialog"] > div > div,
    div[role="dialog"] {
        background-color: #ffffff !important;
        color: #0f172a !important;
        border: 1px solid #cbd5e1 !important;
    }
    div[role="dialog"] h1,
    div[role="dialog"] h2,
    div[role="dialog"] h3,
    div[role="dialog"] p,
    div[role="dialog"] li,
    div[role="dialog"] span,
    div[role="dialog"] strong {
        color: #0f172a !important;
    }
    .status-open {
        background: #dcfce7;
        color: #166534 !important;
        border: 1px solid #86efac;
        border-radius: 8px;
        padding: 10px 14px;
        font-weight: 600;
        margin-bottom: 12px;
    }
    .status-closed {
        background: #fee2e2;
        color: #991b1b !important;
        border: 1px solid #fca5a5;
        border-radius: 8px;
        padding: 10px 14px;
        font-weight: 600;
        margin-bottom: 12px;
    }
    .news-card {
        background: #ffffff;
        border: 1px solid #cbd5e1;
        border-radius: 10px;
        padding: 14px 16px;
        margin-bottom: 10px;
        box-shadow: 0 1px 4px rgba(15, 23, 42, 0.05);
    }
    .news-card a {
        color: #1d4ed8 !important;
        text-decoration: none;
        font-weight: 700;
        font-size: 1rem;
    }
    .news-meta {
        color: #475569 !important;
        font-size: 0.82rem;
        margin-top: 4px;
    }
</style>
"""

DARK_CSS = """
<style>
    :root {
        --background-color: #0e1117;
        --secondary-background-color: #161b22;
        --text-color: #e0e6ed;
        --primary-color: #38bdf8;
    }
    html, body, [data-testid="stAppViewContainer"], .stApp {
        background-color: #0e1117 !important;
        color: #e0e6ed !important;
    }
    header[data-testid="stHeader"] {
        background-color: #0e1117 !important;
    }
    h1, h2, h3, h4, p, span, label, div {
        color: #e0e6ed;
    }
    h1, h2, h3 {
        color: #f1f5f9 !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        font-weight: 700;
    }
    div[data-testid="stRadio"] > div {
        background-color: #161b22 !important;
        padding: 8px 12px;
        border-radius: 10px;
        border: 1px solid #30363d !important;
    }
    div[data-testid="stRadio"] label,
    div[data-testid="stRadio"] label p,
    div[data-testid="stRadio"] span {
        color: #f1f5f9 !important;
        font-weight: 600 !important;
        opacity: 1 !important;
    }
    div[data-testid="stExpander"] {
        background-color: #161b22 !important;
        border: 1px solid #30363d !important;
        border-radius: 10px !important;
    }
    div[data-testid="stExpander"] summary,
    div[data-testid="stExpander"] summary span,
    div[data-testid="stExpander"] summary p {
        background-color: #161b22 !important;
        color: #f1f5f9 !important;
    }
    button[kind="secondary"], div[data-testid="stButton"] > button, a[data-testid="stBaseLinkButton-secondary"] {
        background-color: #161b22 !important;
        color: #f1f5f9 !important;
        border: 1px solid #30363d !important;
        font-weight: 600 !important;
    }
    button[kind="secondary"]:hover, div[data-testid="stButton"] > button:hover {
        background-color: #1f2937 !important;
        border-color: #38bdf8 !important;
    }
    code {
        background-color: #161b22 !important;
        color: #38bdf8 !important;
        border: 1px solid #30363d !important;
        padding: 2px 6px !important;
        border-radius: 5px !important;
    }
    div[data-testid="stMetric"] {
        background: #161b22 !important;
        border: 1px solid #21262d !important;
        border-radius: 8px;
        padding: 12px 16px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }
    div[data-testid="stMetricLabel"], div[data-testid="stMetricLabel"] p {
        color: #8b949e !important;
        font-size: 0.85rem !important;
    }
    div[data-testid="stMetricValue"], div[data-testid="stMetricValue"] div {
        color: #f0f6fc !important;
        font-weight: 600 !important;
    }
    div[data-testid="stDataFrame"] {
        border: 1px solid #30363d !important;
        border-radius: 8px;
        overflow: hidden;
    }
    div[data-testid="stDialog"] > div > div,
    div[role="dialog"] {
        background-color: #161b22 !important;
        color: #e0e6ed !important;
        border: 1px solid #30363d !important;
    }
    div[role="dialog"] h1,
    div[role="dialog"] h2,
    div[role="dialog"] h3,
    div[role="dialog"] p,
    div[role="dialog"] li,
    div[role="dialog"] span,
    div[role="dialog"] strong {
        color: #e0e6ed !important;
    }
    .status-open {
        background: #052e16;
        color: #86efac !important;
        border: 1px solid #166534;
        border-radius: 8px;
        padding: 10px 14px;
        font-weight: 600;
        margin-bottom: 12px;
    }
    .status-closed {
        background: #450a0a;
        color: #fca5a5 !important;
        border: 1px solid #991b1b;
        border-radius: 8px;
        padding: 10px 14px;
        font-weight: 600;
        margin-bottom: 12px;
    }
    .news-card {
        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 10px;
        padding: 14px 16px;
        margin-bottom: 10px;
    }
    .news-card a {
        color: #38bdf8 !important;
        text-decoration: none;
        font-weight: 700;
        font-size: 1rem;
    }
    .news-meta {
        color: #8b949e !important;
        font-size: 0.82rem;
        margin-top: 4px;
    }
</style>
"""


def _sync_streamlit_theme_config(theme_mode: str):
    """Keeps Streamlit's canvas dataframe and dialog portal synced with the toggle."""
    try:
        if theme_mode == "Light":
            st._config.set_option("theme.base", "light")
            st._config.set_option("theme.primaryColor", "#2563eb")
            st._config.set_option("theme.backgroundColor", "#f8fafc")
            st._config.set_option("theme.secondaryBackgroundColor", "#ffffff")
            st._config.set_option("theme.textColor", "#0f172a")
        else:
            st._config.set_option("theme.base", "dark")
            st._config.set_option("theme.primaryColor", "#38bdf8")
            st._config.set_option("theme.backgroundColor", "#0e1117")
            st._config.set_option("theme.secondaryBackgroundColor", "#161b22")
            st._config.set_option("theme.textColor", "#e0e6ed")
    except Exception:
        pass


def apply_theme_css(theme_mode: str):
    _sync_streamlit_theme_config(theme_mode)
    st.markdown(LIGHT_CSS if theme_mode == "Light" else DARK_CSS, unsafe_allow_html=True)


def color_cells(val):
    if isinstance(val, (int, float)):
        if st.session_state.theme_mode == "Light":
            if val > 0:
                return "color: #15803d; font-weight: 700;"
            elif val < 0:
                return "color: #b91c1c; font-weight: 700;"
        else:
            if val > 0:
                return "color: #00E676; font-weight: 600;"
            elif val < 0:
                return "color: #FF5252; font-weight: 600;"
    return ""


def style_market_dataframe(df: pd.DataFrame, theme_mode: str):
    """Applies Light/Dark cell surfaces and green/red % Change colors to the dataframe canvas."""
    if theme_mode == "Light":
        return df.style.set_properties(**{
            "background-color": "#ffffff",
            "color": "#0f172a",
        }).map(color_cells, subset=["% Change"])

    return df.style.set_properties(**{
        "background-color": "#161b22",
        "color": "#e0e6ed",
    }).map(color_cells, subset=["% Change"])
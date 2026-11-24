import streamlit as st

from config.markets import MARKETS
from ui.styles import apply_theme_css
from ui.views import render_index_hub, render_main_dashboard, render_stock_deep_dive

st.set_page_config(page_title="AI Stock Analyzer - Ultra Speed Edition", layout="wide")

if "theme_mode" not in st.session_state:
    st.session_state.theme_mode = "Light"

apply_theme_css(st.session_state.theme_mode)

top_left, top_right = st.columns([4, 1.4])
with top_left:
    st.title("🌐 Global Financial Terminal")
with top_right:
    st.write("")
    chosen_theme = st.radio(
        "Theme:",
        ["☀️ Light", "🌙 Dark"],
        index=0 if st.session_state.theme_mode == "Light" else 1,
        horizontal=True,
        label_visibility="collapsed",
    )
    new_mode = "Light" if "Light" in chosen_theme else "Dark"
    if new_mode != st.session_state.theme_mode:
        st.session_state.theme_mode = new_mode
        apply_theme_css(new_mode)
        st.rerun()

if "symbol" in st.query_params:
    render_stock_deep_dive(st.query_params["symbol"])
elif "index" in st.query_params and st.query_params["index"] in MARKETS:
    render_index_hub(st.query_params["index"])
else:
    render_main_dashboard()
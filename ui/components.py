import time
import plotly.graph_objects as go
import streamlit as st

from services.market_data import get_intraday_history, get_market_status
from services.news import fetch_google_finance_news


def render_market_status_banner(market_key: str) -> bool:
    is_open, local_time_str, hours_label = get_market_status(market_key)
    if is_open:
        st.markdown(
            f'<div class="status-open">🟢 Market Open — Live Feed Active &nbsp;|&nbsp; Local Exchange Time: {local_time_str} &nbsp;|&nbsp; Hours: {hours_label}</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f'<div class="status-closed">🔴 Market Closed — Live data unavailable (showing last available closing data) &nbsp;|&nbsp; Local Exchange Time: {local_time_str} &nbsp;|&nbsp; Hours: {hours_label}</div>',
            unsafe_allow_html=True,
        )
    return is_open


def render_intraday_chart(ticker_symbol: str, curr_sym: str, chart_type: str, is_open: bool):
    st.subheader("Intraday Chart")
    if is_open:
        st.caption(f"⚡ Live Feed Updated: {time.strftime('%H:%M:%S')}")
    else:
        st.caption("⏸️ Market is currently closed — live intraday feed unavailable. Showing last session if available.")

    history = get_intraday_history(ticker_symbol)
    if not history.empty:
        fig = go.Figure()
        is_light = st.session_state.theme_mode == "Light"

        if chart_type == "Candlestick":
            fig.add_trace(go.Candlestick(
                x=history.index,
                open=history["Open"],
                high=history["High"],
                low=history["Low"],
                close=history["Close"],
                name="Candlestick",
                increasing_line_color="#15803d" if is_light else "#00E676",
                decreasing_line_color="#b91c1c" if is_light else "#FF5252",
            ))
        else:
            fig.add_trace(go.Scatter(
                x=history.index,
                y=history["Close"],
                mode="lines",
                name="Close Price",
                line=dict(width=2, color="#2563eb" if is_light else "#00B0FF"),
            ))

        fig.update_layout(
            template="plotly_white" if is_light else "plotly_dark",
            plot_bgcolor="#ffffff" if is_light else "#0e1117",
            paper_bgcolor="#f8fafc" if is_light else "#0e1117",
            font=dict(color="#0f172a" if is_light else "#e0e6ed"),
            xaxis=dict(title="Time", gridcolor="#e2e8f0" if is_light else "#21262d"),
            yaxis=dict(title=f"Price ({curr_sym})", gridcolor="#e2e8f0" if is_light else "#21262d"),
            xaxis_rangeslider_visible=False,
            margin=dict(l=0, r=0, t=30, b=0),
            hovermode="x unified",
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Live intraday chart data is unavailable right now (market closed or no session ticks yet).")


def render_google_finance_news(gf_ticker: str, query_name: str, heading: str):
    head_col, link_col = st.columns([3.5, 1.2])
    gf_url, articles = fetch_google_finance_news(gf_ticker, query_name)

    with head_col:
        st.subheader(heading)
    with link_col:
        st.link_button("📈 Open on Google Finance ↗", gf_url, use_container_width=True)

    if not articles:
        st.info("No recent Google Finance headlines available right now.")
        return

    for art in articles:
        title_html = f'<a href="{art["link"]}" target="_blank">{art["title"]}</a>' if art["link"] else f'<strong>{art["title"]}</strong>'
        meta_parts = [p for p in [art["publisher"], art["pub_time"]] if p]
        meta_str = " • ".join(meta_parts)
        st.markdown(
            f'<div class="news-card">{title_html}<div class="news-meta">{meta_str}</div></div>',
            unsafe_allow_html=True,
        )
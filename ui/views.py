from datetime import datetime
import time

import streamlit as st
import streamlit.components.v1 as components

from config.companies import COMPANY_NAMES
from config.markets import MARKETS
from services.live_tv import fetch_latest_live_video_id, get_market_channel_statuses
from services.market_data import (
    currency_symbol_from_code,
    find_market_key_for_symbol,
    get_market_and_index_bulk,
    get_ticker_info_cached,
)
from services.news import to_google_finance_ticker
from ui.components import (
    render_google_finance_news,
    render_intraday_chart,
    render_market_status_banner,
)
from ui.styles import color_cells


def render_stock_deep_dive(symbol: str):
    if st.button("⬅️ Back to Dashboard"):
        st.query_params.clear()
        st.rerun()

    all_symbols = [s for cfg in MARKETS.values() for s in cfg["symbols"]]
    exact_matches = [s for s in all_symbols if s.split(".")[0] == symbol]
    prefix_matches = [s for s in all_symbols if s.startswith(symbol)]
    ticker_symbol = exact_matches[0] if exact_matches else (prefix_matches[0] if prefix_matches else symbol)

    stock_market_key = find_market_key_for_symbol(ticker_symbol)
    stock_name = COMPANY_NAMES.get(ticker_symbol, symbol)
    gf_ticker = to_google_finance_ticker(ticker_symbol)

    st.header(f"📊 {stock_name} ({symbol}) — Stock Deep Dive")
    is_open = render_market_status_banner(stock_market_key)

    chart_type = st.radio("Select Chart View:", ["Line", "Candlestick"], horizontal=True)
    info = get_ticker_info_cached(ticker_symbol)

    current_price = info.get("currentPrice", info.get("regularMarketPrice", 0)) or 0
    prev_close = info.get("previousClose", 0) or 0
    change = current_price - prev_close
    curr_sym = currency_symbol_from_code(info.get("currency", "USD"))

    st.subheader("Price Action & Fundamentals")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Current Price", f"{curr_sym}{current_price:.2f}", f"{change:+.2f}")
    col2.metric("Today's High", f"{curr_sym}{info.get('dayHigh')}" if info.get("dayHigh") is not None else "N/A")
    col3.metric("Today's Low", f"{curr_sym}{info.get('dayLow')}" if info.get("dayLow") is not None else "N/A")
    col4.metric("Market Cap", f"{curr_sym}{info.get('marketCap', 0) // 10**7} Cr/M" if info.get("marketCap") else "N/A")

    st.divider()

    col5, col6, col7, col8 = st.columns(4)
    col5.metric("P/E Ratio (Trailing)", round(info.get("trailingPE", 0), 2) if info.get("trailingPE") else "N/A")
    col6.metric("EPS (Trailing 12M)", f"{curr_sym}{info.get('trailingEps')}" if info.get("trailingEps") is not None else "N/A")
    col7.metric("Book Value", f"{curr_sym}{info.get('bookValue')}" if info.get("bookValue") is not None else "N/A")
    col8.metric("Price to Book (P/B)", round(info.get("priceToBook", 0), 2) if info.get("priceToBook") else "N/A")

    st.divider()

    col9, col10, col11, col12 = st.columns(4)
    ex_div_timestamp = info.get("exDividendDate")
    formatted_div_date = "N/A"
    if ex_div_timestamp:
        try:
            formatted_div_date = datetime.fromtimestamp(ex_div_timestamp).strftime("%d %b, %Y")
        except Exception:
            formatted_div_date = "N/A"

    div_rate = info.get("dividendRate")
    div_yield = info.get("dividendYield")

    col9.metric("Dividend Rate", f"{curr_sym}{div_rate}" if div_rate else "N/A")
    col10.metric("Dividend Yield", f"{div_yield * 100:.2f}%" if div_yield else "N/A")
    col11.metric("Ex-Dividend Date", formatted_div_date)
    col12.metric("Forward P/E", round(info.get("forwardPE", 0), 2) if info.get("forwardPE") else "N/A")

    st.divider()
    render_intraday_chart(ticker_symbol, curr_sym, chart_type, is_open)

    st.divider()
    render_google_finance_news(gf_ticker, f"{stock_name} {symbol}", f"📰 Google Finance News — {stock_name}")


def render_index_hub(market_key: str):
    if st.button("⬅️ Back to Dashboard"):
        st.query_params.clear()
        st.rerun()

    cfg = MARKETS[market_key]
    idx_ticker = cfg["index_ticker"]
    idx_name = cfg["index_name"]
    currency = cfg["currency"]
    market_channels = cfg["channels"]

    st.header(f"🏛️ {idx_name} ({idx_ticker}) — Market & Live Broadcast Hub")
    is_open = render_market_status_banner(market_key)

    idx_summary, _ = get_market_and_index_bulk((), idx_ticker, idx_name)
    if idx_summary:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Index Value", f"{currency}{idx_summary['price']:,.2f}", f"{idx_summary['change']:+.2f}")
        c2.metric("% Change", f"{idx_summary['p_change']:+.2f}%")
        c3.metric("Volume", f"{idx_summary['volume']:,}" if idx_summary["volume"] > 0 else "N/A")
        c4.metric("Market Sentiment", idx_summary["sentiment"])

    st.divider()

    st.subheader(f"📺 Live Broadcast News — {cfg['title']}")
    ch_state_key = f"active_channel_{market_key}"
    live_statuses = get_market_channel_statuses(market_key)

    if ch_state_key not in st.session_state or st.session_state[ch_state_key] not in market_channels:
        live_first = next((name for name in market_channels if live_statuses.get(name, False)), None)
        st.session_state[ch_state_key] = live_first or list(market_channels.keys())[0]

    main_col, side_col = st.columns([3, 1], gap="large")

    with main_col:
        active_ch_name = st.session_state[ch_state_key]
        active_ch_id = market_channels.get(active_ch_name)
        st.markdown(f"#### 🔴 LIVE: {active_ch_name}")

        video_id = fetch_latest_live_video_id(active_ch_id)
        if video_id:
            embed_url = f"https://www.youtube.com/embed/{video_id}?autoplay=1&mute=0&rel=0"
            iframe_html = f"""
                <iframe
                    width="100%"
                    height="520"
                    src="{embed_url}"
                    title="{active_ch_name} Live Stream"
                    frameborder="0"
                    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
                    allowfullscreen
                    style="border-radius: 12px; box-shadow: 0 8px 24px rgba(0,0,0,0.2);">
                </iframe>
            """
            components.html(iframe_html, height=540)
            st.caption(f"Broadcasting via Stream ID: `{video_id}`")
        else:
            st.warning(
                f"Could not locate an active live stream feed for **{active_ch_name}**. "
                "They may be temporarily offline — pick a 🟢 Live channel on the right."
            )

    @st.fragment(run_every="60s")
    def render_index_channel_menu():
        statuses = get_market_channel_statuses(market_key)
        st.markdown("#### Channels")
        st.caption("🟢 Live Broadcast | 🔴 Offline")

        for ch_name in market_channels.keys():
            is_active = ch_name == st.session_state[ch_state_key]
            is_live = statuses.get(ch_name, False)
            icon = "🟢" if is_live else "🔴"
            btn_label = f"▶ {icon} {ch_name}" if is_active else f"{icon} {ch_name}"

            if st.button(
                label=btn_label,
                use_container_width=True,
                type="primary" if is_active else "secondary",
                key=f"idx_ch_{market_key}_{ch_name}",
            ):
                st.session_state[ch_state_key] = ch_name
                st.rerun()

    with side_col:
        with st.container(height=560, border=False):
            render_index_channel_menu()

    st.divider()

    chart_type = st.radio("Select Index Chart View:", ["Line", "Candlestick"], horizontal=True)
    render_intraday_chart(idx_ticker, currency, chart_type, is_open)

    st.divider()
    render_google_finance_news(cfg["gf_index_ticker"], idx_name, f"📰 Google Finance Market News — {idx_name}")


def render_main_dashboard():
    st.markdown("Ultra-fast live volume, index pulse, % change, and sentiment tracking across international markets.")

    with st.expander("⚙️ Terminal Settings & Auto-Refresh Controls"):
        col_set1, col_set2 = st.columns([3, 1])
        with col_set1:
            refresh_rate = st.slider("Auto-Refresh Interval (seconds)", min_value=5, max_value=60, value=15)
        with col_set2:
            st.write("")
            if st.button("🔄 Manual Refresh Now"):
                st.cache_data.clear()
                st.rerun()

    market_keys = list(MARKETS.keys())
    market_labels = [MARKETS[k]["label"] for k in market_keys]
    selected_label = st.radio("Select Market Exchange:", market_labels, horizontal=True)
    selected_key = market_keys[market_labels.index(selected_label)]

    @st.fragment(run_every=refresh_rate)
    def render_market_pipeline(m_key: str):
        cfg = MARKETS[m_key]
        currency = cfg["currency"]

        st.header(cfg["title"])
        st.caption(cfg["desc"])
        is_open = render_market_status_banner(m_key)

        idx_data, df = get_market_and_index_bulk(tuple(cfg["symbols"]), cfg["index_ticker"], cfg["index_name"])

        if st.button(
            f"📌 {cfg['index_name']} ({cfg['index_ticker']}) — Click for Live TV News, Google Finance Headlines & Chart ↗",
            use_container_width=True,
            key=f"open_idx_{m_key}",
        ):
            st.query_params["index"] = m_key
            st.rerun()

        if idx_data:
            ic1, ic2, ic3, ic4 = st.columns(4)
            ic1.metric("Index Value", f"{currency}{idx_data['price']:,.2f}", f"{idx_data['change']:+.2f}")
            ic2.metric("% Change", f"{idx_data['p_change']:+.2f}%")
            ic3.metric("Volume", f"{idx_data['volume']:,}" if idx_data["volume"] > 0 else "N/A")
            ic4.metric("Index Sentiment", idx_data["sentiment"])
        else:
            st.info(f"Index quote for {cfg['index_name']} is currently unavailable.")

        st.divider()

        if not df.empty:
            if is_open:
                st.write(f"⚡ **Live Bulk Feed Updated:** `{time.strftime('%H:%M:%S')}` (Auto-refresh every {refresh_rate}s)")
            else:
                st.write(f"⏸️ **Last Checked:** `{time.strftime('%H:%M:%S')}` — *Market Closed (Live data unavailable)*")

            if st.session_state.theme_mode == "Light":
                styled = df.style.set_properties(**{
                    "background-color": "#ffffff",
                    "color": "#0f172a",
                }).map(color_cells, subset=["% Change"])
            else:
                styled = df.style.set_properties(**{
                    "background-color": "#161b22",
                    "color": "#e0e6ed",
                }).map(color_cells, subset=["% Change"])

            
            st.dataframe(
                styled,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Ticker": st.column_config.LinkColumn("Ticker", display_text=r"#(.+)$"),
                    "Stock Name": st.column_config.TextColumn("Stock Name"),
                    "Price": st.column_config.NumberColumn("Price", format=f"{currency}%.2f"),
                    "% Change": st.column_config.NumberColumn("% Change", format="%.2f%%"),
                    "Volume": st.column_config.NumberColumn("Volume", format="%d"),
                    "Market Sentiment": st.column_config.TextColumn("Market Sentiment"),
                },
            )
        else:
            st.warning("Fetching market data... please wait.")

    render_market_pipeline(selected_key)
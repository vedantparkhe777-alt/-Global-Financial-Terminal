import concurrent.futures
from datetime import datetime
import time

import streamlit as st
import streamlit.components.v1 as components

from config.companies import COMPANY_NAMES
from config.markets import MARKETS
from services.ai_agent import generate_ai_stock_report
from services.live_tv import get_market_channel_video_ids
from services.market_data import (
    currency_symbol_from_code,
    find_market_key_for_symbol,
    get_intraday_history,
    get_market_and_index_bulk,
    get_market_status,
    get_ticker_info_cached,
    resolve_full_symbol,
)
from services.news import fetch_google_finance_news, to_google_finance_ticker
from ui.components import (
    render_google_finance_news,
    render_intraday_chart,
    render_market_status_banner,
)
from ui.styles import style_market_dataframe


def _close_ai_modal():
    st.session_state.pop("ai_modal_symbol", None)


@st.dialog("⭐ AI Agent Stock & Commodity Report", width="large", on_dismiss=_close_ai_modal)
def show_ai_agent_dialog(ticker_symbol: str):
    stock_name = COMPANY_NAMES.get(ticker_symbol, ticker_symbol)
    st.subheader(f"{stock_name} ({ticker_symbol})")

    with st.spinner("Running technical indicators, scanning headlines, and synthesizing AI report..."):
        report = generate_ai_stock_report(ticker_symbol)

    if "error" in report:
        st.error(report["error"])
        return

    tech = report["tech"]
    c = report["curr_sym"]

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Current Price", f"{c}{tech['current_price']:,.2f}")
    m2.metric("Entry Zone", f"{c}{tech['entry_low']:,.2f} – {c}{tech['entry_high']:,.2f}")
    m3.metric("Stop-Loss", f"{c}{tech['stop_loss']:,.2f}")
    m4.metric("Targets (T1 / T2)", f"{c}{tech['target_1']:,.2f} / {c}{tech['target_2']:,.2f}")

    st.caption(
        f"RSI (14): **{tech['rsi14']}** • 20D Support: **{c}{tech['support_20d']:,.2f}** • "
        f"20D Resistance: **{c}{tech['resistance_20d']:,.2f}** • Powered by **{report['powered_by']}**"
    )
    st.divider()
    st.markdown(report["markdown"])
    st.divider()

    col_a, col_b = st.columns([2, 1])
    with col_a:
        st.caption("⚠️ *AI-generated summary & levels are for informational purposes only, not financial advice.*")
    with col_b:
        if st.button("📊 Full Chart & Fundamentals ↗", use_container_width=True):
            st.session_state.pop("ai_modal_symbol", None)
            st.query_params["symbol"] = ticker_symbol
            st.rerun()


def render_stock_deep_dive(symbol: str):
    if st.button("⬅️ Back to Dashboard"):
        st.query_params.clear()
        st.rerun()

    ticker_symbol = resolve_full_symbol(symbol)
    stock_market_key = find_market_key_for_symbol(ticker_symbol)
    stock_name = COMPANY_NAMES.get(ticker_symbol, ticker_symbol)
    gf_ticker = to_google_finance_ticker(ticker_symbol)

    st.header(f"📊 {stock_name} ({ticker_symbol}) — Deep Dive")
    is_open = render_market_status_banner(stock_market_key)

    chart_type = st.radio("Select Chart View:", ["Line", "Candlestick"], horizontal=True)

    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        f_info = executor.submit(get_ticker_info_cached, ticker_symbol)
        f_hist = executor.submit(get_intraday_history, ticker_symbol)
        f_news = executor.submit(fetch_google_finance_news, gf_ticker, f"{stock_name} {ticker_symbol}")
        info = f_info.result()
        intraday_df = f_hist.result()
        prefetched_news = f_news.result()

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
    render_intraday_chart(ticker_symbol, curr_sym, chart_type, is_open, history=intraday_df)

    st.divider()
    render_google_finance_news(
        gf_ticker,
        f"{stock_name} {ticker_symbol}",
        f"📰 Google Finance News — {stock_name}",
        prefetched_news=prefetched_news,
    )


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
    live_video_ids = get_market_channel_video_ids(market_key)

    if ch_state_key not in st.session_state or st.session_state[ch_state_key] not in market_channels:
        live_first = next((name for name in market_channels if live_video_ids.get(name)), None)
        st.session_state[ch_state_key] = live_first or list(market_channels.keys())[0]

    main_col, side_col = st.columns([3, 1], gap="large")

    with main_col:
        active_ch_name = st.session_state[ch_state_key]
        video_id = live_video_ids.get(active_ch_name)
        st.markdown(f"#### 🔴 LIVE: {active_ch_name}")

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

    @st.fragment(run_every="120s")
    def render_index_channel_menu():
        video_ids = get_market_channel_video_ids(market_key)
        st.markdown("#### Channels")
        st.caption("🟢 Live Broadcast | 🔴 Offline")

        for ch_name in market_channels.keys():
            is_active = ch_name == st.session_state[ch_state_key]
            is_live = bool(video_ids.get(ch_name))
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

    if "ai_table_nonce" not in st.session_state:
        st.session_state.ai_table_nonce = 0

    with st.expander("⚙️ Terminal Settings & Auto-Refresh Controls"):
        col_set1, col_set2 = st.columns([3, 1])
        with col_set1:
            refresh_rate = st.slider("Auto-Refresh Interval (seconds)", min_value=5, max_value=60, value=15)
        with col_set2:
            st.write("")
            if st.button("🔄 Manual Refresh Now"):
                get_market_and_index_bulk.clear()
                st.rerun()

    market_keys = list(MARKETS.keys())
    market_labels = [MARKETS[k]["label"] for k in market_keys]
    selected_label = st.radio("Select Market Exchange:", market_labels, horizontal=True)
    selected_key = market_keys[market_labels.index(selected_label)]

    is_market_open, _, _ = get_market_status(selected_key)
    modal_open = bool(st.session_state.get("ai_modal_symbol"))
    effective_refresh = refresh_rate if (is_market_open and not modal_open) else None

    @st.fragment(run_every=effective_refresh)
    def render_market_pipeline(m_key: str):
        cfg = MARKETS[m_key]
        currency = cfg["currency"]
        table_key = f"market_table_{m_key}_{st.session_state.theme_mode}_{st.session_state.ai_table_nonce}"

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
                st.write(
                    f"⚡ **Live Bulk Feed Updated:** `{time.strftime('%H:%M:%S')}` "
                    f"(Auto-refresh every {refresh_rate}s • Click any **⭐** cell for AI Analysis)"
                )
            else:
                st.write(
                    f"⏸️ **Last Checked:** `{time.strftime('%H:%M:%S')}` — *Market Closed* "
                    "(Click any **⭐** cell for AI Analysis)"
                )

            styled_df = style_market_dataframe(df, st.session_state.theme_mode)

            event = st.dataframe(
                styled_df,
                use_container_width=True,
                hide_index=True,
                on_select="rerun",
                selection_mode="single-cell",
                key=table_key,
                column_order=[
                    "Ticker",
                    "Stock Name",
                    "Price",
                    "% Change",
                    "Volume",
                    "Market Sentiment",
                    "AI Agent",
                ],
                column_config={
                    "Ticker": st.column_config.LinkColumn("Ticker", display_text=r"#(.+)$"),
                    "Stock Name": st.column_config.TextColumn("Stock Name"),
                    "Price": st.column_config.NumberColumn("Price", format=f"{currency}%.2f"),
                    "% Change": st.column_config.NumberColumn("% Change", format="%.2f%%"),
                    "Volume": st.column_config.NumberColumn("Volume", format="%d"),
                    "Market Sentiment": st.column_config.TextColumn("Market Sentiment"),
                    "AI Agent": st.column_config.TextColumn(
                        "AI Agent",
                        help="Click any ⭐ cell to open an in-page AI Summary, Pros/Cons & Entry/Exit Plan",
                        width="small",
                    ),
                },
            )

            selected_cells = getattr(getattr(event, "selection", None), "cells", []) or []
            if selected_cells:
                cell = selected_cells[0]
                row_idx = cell[0] if isinstance(cell, (tuple, list)) else cell.get("row")
                col_name = cell[1] if isinstance(cell, (tuple, list)) else cell.get("column")
                if col_name == "AI Agent" and row_idx is not None and 0 <= row_idx < len(df):
                    st.session_state["ai_modal_symbol"] = df.iloc[row_idx]["_symbol"]
                    st.session_state.ai_table_nonce += 1
                    st.rerun()
        else:
            st.warning("Fetching market data... please wait.")

    render_market_pipeline(selected_key)

    if st.session_state.get("ai_modal_symbol"):
        show_ai_agent_dialog(st.session_state["ai_modal_symbol"])
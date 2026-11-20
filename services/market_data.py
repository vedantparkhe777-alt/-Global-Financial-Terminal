from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import pandas as pd
import streamlit as st
import yfinance as yf

from config.companies import COMPANY_NAMES
from config.markets import MARKETS


def get_market_status(market_key: str):
    cfg = MARKETS[market_key]
    try:
        now_local = datetime.now(ZoneInfo(cfg["tz"]))
    except Exception:
        now_local = datetime.now(timezone(timedelta(hours=cfg["utc_offset"])))

    is_weekday = now_local.weekday() < 5
    current_hm = (now_local.hour, now_local.minute)
    in_session = any(start <= current_hm <= end for start, end in cfg["sessions"])
    is_open = is_weekday and in_session
    local_time_str = now_local.strftime("%a %H:%M")

    return is_open, local_time_str, cfg["hours_label"]


def find_market_key_for_symbol(ticker_symbol: str) -> str:
    for key, cfg in MARKETS.items():
        if ticker_symbol in cfg["symbols"] or ticker_symbol == cfg["index_ticker"]:
            return key
    return "Nasdaq"


def classify_sentiment(p_change: float) -> str:
    if p_change >= 1.5:
        return "🟢 Strong Bullish"
    elif p_change > 0:
        return "📈 Leaning Bullish"
    elif p_change <= -1.5:
        return "🔴 Strong Bearish"
    elif p_change < 0:
        return "📉 Leaning Bearish"
    return "⚖️ Neutral"


def _extract_ticker_slice(data: pd.DataFrame, symbol: str, multi: bool) -> pd.DataFrame:
    if data is None or data.empty:
        return pd.DataFrame()
    if isinstance(data.columns, pd.MultiIndex):
        if multi and symbol in data.columns.get_level_values(0):
            return data[symbol]
        if symbol in data.columns.get_level_values(-1):
            return data.xs(symbol, axis=1, level=-1)
    return data


@st.cache_data(ttl=15)
def get_market_and_index_bulk(symbols: tuple[str, ...], index_symbol: str, index_name: str):
    """Fetch index + all constituent stocks in ONE single yf.download() request."""
    all_tickers = [index_symbol] + list(symbols)
    data = yf.download(all_tickers, period="2d", interval="1d", group_by="ticker", progress=False)
    is_multi = len(all_tickers) > 1

    index_summary = None
    try:
        df_idx = _extract_ticker_slice(data, index_symbol, multi=is_multi)
        if not df_idx.empty and "Close" in df_idx.columns:
            df_idx = df_idx.dropna(subset=["Close"])
            if len(df_idx) >= 2:
                idx_prev = float(df_idx["Close"].iloc[-2])
                idx_curr = float(df_idx["Close"].iloc[-1])
                if idx_prev != 0:
                    idx_vol = (
                        int(df_idx["Volume"].iloc[-1])
                        if "Volume" in df_idx.columns and pd.notna(df_idx["Volume"].iloc[-1])
                        else 0
                    )
                    idx_change = idx_curr - idx_prev
                    idx_p_change = (idx_change / idx_prev) * 100
                    index_summary = {
                        "name": index_name,
                        "ticker": index_symbol,
                        "price": idx_curr,
                        "change": idx_change,
                        "p_change": idx_p_change,
                        "volume": idx_vol,
                        "sentiment": classify_sentiment(idx_p_change),
                    }
    except Exception:
        index_summary = None

    records = []
    for symbol in symbols:
        try:
            clean_symbol = symbol.split(".")[0]
            stock_display_name = COMPANY_NAMES.get(symbol, clean_symbol)

            df_ticker = _extract_ticker_slice(data, symbol, multi=is_multi)
            if df_ticker.empty or "Close" not in df_ticker.columns:
                continue

            df_ticker = df_ticker.dropna(subset=["Close"])
            if len(df_ticker) < 2:
                continue

            prev_close = float(df_ticker["Close"].iloc[-2])
            curr_price = float(df_ticker["Close"].iloc[-1])
            volume = (
                int(df_ticker["Volume"].iloc[-1])
                if "Volume" in df_ticker.columns and pd.notna(df_ticker["Volume"].iloc[-1])
                else 0
            )
            if prev_close == 0:
                continue

            p_change = ((curr_price - prev_close) / prev_close) * 100

            records.append({
                "Ticker": f"/?symbol={clean_symbol}#{clean_symbol}",
                "Stock Name": stock_display_name,
                "Price": curr_price,
                "% Change": p_change,
                "Volume": volume,
                "Market Sentiment": classify_sentiment(p_change),
            })
        except Exception:
            pass

    df = pd.DataFrame(records)
    if not df.empty:
        df = df.sort_values(by="Volume", ascending=False)

    return index_summary, df


@st.cache_data(ttl=60)
def get_ticker_info_cached(ticker_symbol: str) -> dict:
    try:
        return yf.Ticker(ticker_symbol).info or {}
    except Exception:
        return {}


@st.cache_data(ttl=30)
def get_intraday_history(ticker_symbol: str) -> pd.DataFrame:
    try:
        return yf.Ticker(ticker_symbol).history(period="1d", interval="1m")
    except Exception:
        return pd.DataFrame()


def currency_symbol_from_code(currency: str) -> str:
    if currency == "INR":
        return "₹"
    elif currency == "EUR":
        return "€"
    elif currency in ["CNY", "JPY"]:
        return "¥"
    elif currency == "KRW":
        return "₩"
    elif currency == "HKD":
        return "HK$"
    return "$"
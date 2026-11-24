import concurrent.futures
import os

import pandas as pd
import streamlit as st
import yfinance as yf

from config.companies import COMPANY_NAMES
from services.market_data import currency_symbol_from_code, get_ticker_info_cached
from services.news import fetch_google_finance_news, to_google_finance_ticker


@st.cache_data(ttl=300)
def get_technical_snapshot(ticker_symbol: str) -> dict:
    """Computes real technical indicators and support/resistance levels from 6-month daily bars."""
    df = yf.Ticker(ticker_symbol).history(period="6mo", interval="1d", auto_adjust=False)
    if df is None or df.empty or len(df) < 15:
        return {}

    close = df["Close"].dropna()
    high = df["High"].dropna()
    low = df["Low"].dropna()

    curr = float(close.iloc[-1])
    sma20 = float(close.rolling(20).mean().iloc[-1]) if len(close) >= 20 else curr
    sma50 = float(close.rolling(50).mean().iloc[-1]) if len(close) >= 50 else sma20
    sma200 = float(close.rolling(200).mean().iloc[-1]) if len(close) >= 200 else None

    # 14-day RSI
    delta = close.diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = (-delta.clip(upper=0)).rolling(14).mean()
    rs = gain / loss.replace(0, pd.NA)
    rsi = float((100 - (100 / (1 + rs))).iloc[-1]) if pd.notna(rs.iloc[-1]) else 50.0

    # 14-day ATR for realistic stop-loss & target zones
    tr = pd.concat([
        high - low,
        (high - close.shift(1)).abs(),
        (low - close.shift(1)).abs(),
    ], axis=1).max(axis=1)
    atr = float(tr.rolling(14).mean().iloc[-1]) if len(tr) >= 14 else curr * 0.02

    support_20d = float(low.tail(20).min())
    resistance_20d = float(high.tail(20).max())

    return {
        "current_price": round(curr, 2),
        "sma20": round(sma20, 2),
        "sma50": round(sma50, 2),
        "sma200": round(sma200, 2) if sma200 else None,
        "rsi14": round(rsi, 2),
        "atr14": round(atr, 2),
        "support_20d": round(support_20d, 2),
        "resistance_20d": round(resistance_20d, 2),
        "entry_low": round(max(support_20d, curr - 0.6 * atr), 2),
        "entry_high": round(curr, 2),
        "stop_loss": round(max(0.01, support_20d - 0.8 * atr), 2),
        "target_1": round(max(resistance_20d, curr + 1.5 * atr), 2),
        "target_2": round(max(resistance_20d + atr, curr + 3.0 * atr), 2),
    }


def _get_gemini_api_key() -> str | None:
    try:
        if "GEMINI_API_KEY" in st.secrets:
            return st.secrets["GEMINI_API_KEY"]
    except Exception:
        pass
    return os.getenv("GEMINI_API_KEY")


def _fallback_report(stock_name: str, ticker: str, curr_sym: str, tech: dict, info: dict) -> str:
    trend = "Bullish" if tech["current_price"] >= tech["sma50"] else "Bearish / Pullback"
    rsi_note = (
        "Overbought (>70 — wait for pullback)"
        if tech["rsi14"] > 70
        else "Oversold (<30 — potential bounce)"
        if tech["rsi14"] < 30
        else "Neutral momentum"
    )
    return f"""
### Executive Summary
**{stock_name} (`{ticker}`)** is currently trading at **{curr_sym}{tech['current_price']:,.2f}** with a **{trend}** medium-term structure relative to its 50-DMA ({curr_sym}{tech['sma50']:,.2f}). 14-day RSI sits at **{tech['rsi14']}** ({rsi_note}).

### Key Pros (Bull Case)
* Price action vs 20-DMA ({curr_sym}{tech['sma20']:,.2f}) and 50-DMA ({curr_sym}{tech['sma50']:,.2f}) gives clear trend reference.
* Well-defined 20-day support floor near **{curr_sym}{tech['support_20d']:,.2f}**.
* Trailing P/E: **{info.get('trailingPE', 'N/A')}** | Sector: **{info.get('sector', 'Commodity / Index')}**.

### Key Cons & Risks (Bear Case)
* Overhead resistance sits near **{curr_sym}{tech['resistance_20d']:,.2f}**.
* Daily volatility (14-day ATR) is **{curr_sym}{tech['atr14']:,.2f}** per session—position sizing should account for swings.

### Suggested Entry & Exit Plan (Technical Model)
* **Entry Zone:** {curr_sym}{tech['entry_low']:,.2f} – {curr_sym}{tech['entry_high']:,.2f}
* **Stop-Loss:** {curr_sym}{tech['stop_loss']:,.2f}
* **Target 1 (Short-Term):** {curr_sym}{tech['target_1']:,.2f}
* **Target 2 (Swing):** {curr_sym}{tech['target_2']:,.2f}
"""


@st.cache_data(ttl=600, show_spinner=False)
def _query_gemini_cached(ticker_symbol: str, prompt: str, api_key: str) -> str:
    """Cached only on success so transient errors are never cached."""
    from google import genai

    client = genai.Client(api_key=api_key)
    if hasattr(client, "interactions"):
        interaction = client.interactions.create(
            model="gemini-3.8-flash",
            input=prompt,
            generation_config={"thinking_level": "low"},
        )
        return interaction.output_text

    response = client.models.generate_content(
        model="gemini-3.8-flash",
        contents=prompt,
    )
    return response.text


def generate_ai_stock_report(ticker_symbol: str) -> dict:
    stock_name = COMPANY_NAMES.get(ticker_symbol, ticker_symbol)
    gf_ticker = to_google_finance_ticker(ticker_symbol)

    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        f_tech = executor.submit(get_technical_snapshot, ticker_symbol)
        f_info = executor.submit(get_ticker_info_cached, ticker_symbol)
        f_news = executor.submit(fetch_google_finance_news, gf_ticker, f"{stock_name} {ticker_symbol}", 5)
        tech = f_tech.result()
        info = f_info.result()
        _, articles = f_news.result()

    curr_sym = currency_symbol_from_code(info.get("currency", "USD"))
    if not tech:
        return {"error": f"Insufficient historical price data for {ticker_symbol}."}

    api_key = _get_gemini_api_key()
    if not api_key:
        return {
            "stock_name": stock_name,
            "curr_sym": curr_sym,
            "tech": tech,
            "info": info,
            "markdown": _fallback_report(stock_name, ticker_symbol, curr_sym, tech, info),
            "powered_by": "Quantitative Technical Engine (No Gemini API Key)",
        }

    headlines_text = "\n".join(f"- {a['title']} ({a['publisher']})" for a in articles) or "No recent headlines."
    is_commodity = ticker_symbol.endswith("=F")

    fundamentals_block = (
        "Asset Type: Global Commodity Futures (focus on macro supply/demand, USD, rates, and technical levels)."
        if is_commodity
        else (
            f"Sector: {info.get('sector', 'N/A')} | Industry: {info.get('industry', 'N/A')}\n"
            f"Market Cap: {info.get('marketCap', 'N/A')} | Trailing P/E: {info.get('trailingPE', 'N/A')} | "
            f"Forward P/E: {info.get('forwardPE', 'N/A')} | P/B: {info.get('priceToBook', 'N/A')}\n"
            f"ROE: {info.get('returnOnEquity', 'N/A')} | Profit Margin: {info.get('profitMargins', 'N/A')} | "
            f"Debt/Equity: {info.get('debtToEquity', 'N/A')} | 52W Range: {info.get('fiftyTwoWeekLow', 'N/A')} - {info.get('fiftyTwoWeekHigh', 'N/A')}"
        )
    )

    prompt = f"""
You are a concise, institutional-grade equity & commodities research analyst.
Analyze {stock_name} ({ticker_symbol}) strictly using the live data below. Currency: {curr_sym}.

LIVE TECHNICAL DATA:
- Current Price: {curr_sym}{tech['current_price']}
- 20-DMA: {curr_sym}{tech['sma20']} | 50-DMA: {curr_sym}{tech['sma50']} | 200-DMA: {curr_sym}{tech['sma200']}
- 14-day RSI: {tech['rsi14']} | 14-day ATR: {curr_sym}{tech['atr14']}
- 20-day Support: {curr_sym}{tech['support_20d']} | 20-day Resistance: {curr_sym}{tech['resistance_20d']}
- Baseline Levels -> Entry: {curr_sym}{tech['entry_low']}–{curr_sym}{tech['entry_high']}, Stop-Loss: {curr_sym}{tech['stop_loss']}, Target 1: {curr_sym}{tech['target_1']}, Target 2: {curr_sym}{tech['target_2']}

FUNDAMENTALS / CONTEXT:
{fundamentals_block}

RECENT HEADLINES:
{headlines_text}

Format your response cleanly in Markdown with these exact sections:
### Executive Summary
(3-4 crisp sentences on trend, valuation/macro context, and current catalyst.)

### Key Pros (Bull Case)
(3-4 concrete bullet points referencing the data/news above.)

### Key Cons & Risks (Bear Case)
(3-4 concrete bullet points referencing valuation, technical, or headline risks.)

### Actionable Entry & Exit Plan
- **Verdict:** (Accumulate / Buy on Dip / Hold / Wait / Avoid)
- **Ideal Entry Zone:** (specific price range in {curr_sym} with brief rationale)
- **Stop-Loss:** (specific level in {curr_sym} tied to support/ATR)
- **Exit Targets:** Target 1 & Target 2 in {curr_sym} with Risk:Reward ratio
"""

    try:
        md_text = _query_gemini_cached(ticker_symbol, prompt, api_key)
        powered_by = "Gemini 3.8 Flash AI Agent"
    except Exception as e:
        md_text = _fallback_report(stock_name, ticker_symbol, curr_sym, tech, info) + f"\n\n> ⚠️ Gemini fallback triggered: `{e}`"
        powered_by = "Fallback Engine"

    return {
        "stock_name": stock_name,
        "curr_sym": curr_sym,
        "tech": tech,
        "info": info,
        "markdown": md_text,
        "powered_by": powered_by,
    }
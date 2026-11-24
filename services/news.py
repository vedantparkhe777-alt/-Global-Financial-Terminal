import urllib.parse
import xml.etree.ElementTree as ET

import streamlit as st

from config.markets import MARKETS
from services.live_tv import get_http_session

try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None

SUFFIX_TO_GF_EXCHANGE = {
    ".NS": "NSE",
    ".AS": "AMS",
    ".PA": "EPA",
    ".DE": "ETR",
    ".MC": "BME",
    ".MI": "BIT",
    ".BR": "EBR",
    ".L": "LON",
    ".HE": "HEL",
    ".SS": "SHA",
    ".SZ": "SHE",
    ".HK": "HKG",
    ".T": "TYO",
    ".KS": "KRX",
}


def to_google_finance_ticker(yf_symbol: str) -> str:
    for cfg in MARKETS.values():
        if yf_symbol == cfg["index_ticker"]:
            return cfg["gf_index_ticker"]

    if yf_symbol.endswith("=F"):
        return yf_symbol

    for suffix, exchange in SUFFIX_TO_GF_EXCHANGE.items():
        if yf_symbol.endswith(suffix):
            base = yf_symbol[: -len(suffix)]
            return f"{base}:{exchange}"

    return f"{yf_symbol}:NASDAQ"


@st.cache_data(ttl=180)
def fetch_google_finance_news(gf_ticker: str, query_name: str, limit: int = 8):
    """Fetches news from Google Finance quote page first, with Google News RSS fallback."""
    articles = []
    is_commodity = gf_ticker.endswith("=F")
    gf_url = (
        f"https://www.google.com/finance/markets/commodities?hl=en"
        if is_commodity
        else f"https://www.google.com/finance/quote/{gf_ticker}?hl=en"
    )
    session = get_http_session()

    if BeautifulSoup is not None and not is_commodity:
        try:
            resp = session.get(gf_url, timeout=4)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, "html.parser")
                seen = set()
                for card in soup.select("div.yY3Lee, div.z4rs2b, div.LIT7If"):
                    link_el = card.find("a", href=True)
                    title_el = card.select_one("div.Yfwt5, div.mCBkyc, a")
                    source_el = card.select_one("div.sfyJob, div.AYbnrd")
                    time_el = card.select_one("div.Adak, div.ZE0LJd")
                    if link_el and title_el:
                        title = title_el.get_text(" ", strip=True)
                        href = link_el["href"]
                        if title and href.startswith("http") and title not in seen:
                            seen.add(title)
                            articles.append({
                                "title": title,
                                "link": href,
                                "publisher": source_el.get_text(" ", strip=True) if source_el else "Google Finance",
                                "pub_time": time_el.get_text(" ", strip=True) if time_el else "",
                            })
                            if len(articles) >= limit:
                                break
        except Exception:
            pass

    if not articles:
        try:
            search_topic = (
                f"{query_name} commodity price OR market"
                if is_commodity
                else f"{query_name} stock OR market"
            )
            encoded_q = urllib.parse.quote(search_topic)
            rss_url = f"https://news.google.com/rss/search?q={encoded_q}&hl=en-IN&gl=IN&ceid=IN:en"
            resp = session.get(rss_url, timeout=4)
            if resp.status_code == 200:
                root = ET.fromstring(resp.content)
                for item in root.findall(".//item")[:limit]:
                    title_el = item.find("title")
                    link_el = item.find("link")
                    pub_el = item.find("pubDate")
                    src_el = item.find("source")

                    title = title_el.text.strip() if title_el is not None and title_el.text else ""
                    link = link_el.text.strip() if link_el is not None and link_el.text else ""
                    publisher = src_el.text.strip() if src_el is not None and src_el.text else "Google Finance / News"
                    pub_time = pub_el.text.strip()[:22] if pub_el is not None and pub_el.text else ""

                    if title:
                        articles.append({
                            "title": title,
                            "link": link,
                            "publisher": publisher,
                            "pub_time": pub_time,
                        })
        except Exception:
            pass

    return gf_url, articles
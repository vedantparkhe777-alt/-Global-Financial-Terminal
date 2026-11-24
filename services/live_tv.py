import concurrent.futures
import xml.etree.ElementTree as ET

import requests
import streamlit as st

from config.markets import MARKETS


@st.cache_resource
def get_http_session() -> requests.Session:
    """Shared HTTP session with connection pooling across reruns."""
    session = requests.Session()
    session.headers.update({
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/128.0.0.0 Safari/537.36"
        )
    })
    return session


def fetch_latest_live_video_id(channel_id: str) -> str | None:
    """Fetches the exact video ID of the current live stream using YouTube's UULV playlist RSS."""
    if not channel_id or not channel_id.startswith("UC"):
        return None

    playlist_id = "UULV" + channel_id[2:]
    rss_url = f"https://www.youtube.com/feeds/videos.xml?playlist_id={playlist_id}"

    try:
        response = get_http_session().get(rss_url, timeout=3)
        if response.status_code == 200:
            root = ET.fromstring(response.content)
            atom_ns = "{http://www.w3.org/2005/Atom}"
            yt_ns = {"yt": "http://www.youtube.com/xml/schemas/2015"}

            entry = root.find(f"{atom_ns}entry")
            if entry is not None:
                video_id_elem = entry.find("yt:videoId", yt_ns)
                if video_id_elem is not None:
                    return video_id_elem.text
    except Exception:
        pass
    return None


@st.cache_data(ttl=120)
def get_market_channel_video_ids(market_key: str) -> dict[str, str | None]:
    """Concurrently fetches live video IDs (or None if offline) for all channels in a market."""
    channels = MARKETS[market_key]["channels"]
    results: dict[str, str | None] = {}

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_map = {
            executor.submit(fetch_latest_live_video_id, cid): name
            for name, cid in channels.items()
        }
        for future in concurrent.futures.as_completed(future_map):
            name = future_map[future]
            results[name] = future.result()

    return results
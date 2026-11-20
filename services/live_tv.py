import concurrent.futures
import xml.etree.ElementTree as ET

import requests
import streamlit as st

from config.markets import MARKETS


def fetch_latest_live_video_id(channel_id: str):
    """Fetches the exact video ID of the current live stream using YouTube's UULV playlist RSS."""
    if not channel_id or not channel_id.startswith("UC"):
        return None

    playlist_id = "UULV" + channel_id[2:]
    rss_url = f"https://www.youtube.com/feeds/videos.xml?playlist_id={playlist_id}"

    try:
        response = requests.get(rss_url, timeout=4)
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


@st.cache_data(ttl=60)
def get_market_channel_statuses(market_key: str):
    """Concurrently checks live status for all channels assigned to a market."""
    channels = MARKETS[market_key]["channels"]
    results = {}

    def check_status(name, cid):
        return name, bool(fetch_latest_live_video_id(cid))

    with concurrent.futures.ThreadPoolExecutor(max_workers=12) as executor:
        futures = [executor.submit(check_status, name, cid) for name, cid in channels.items()]
        for future in concurrent.futures.as_completed(futures):
            name, is_live = future.result()
            results[name] = is_live

    return results
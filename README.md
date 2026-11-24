Here is your updated `README.md` reflecting the new **Global Commodities** market tab, the **⭐ Gemini 3.8 Flash AI Agent** in-page modal, the **performance & anti-ghosting upgrades**, and the updated project structure:

```markdown
# 🌐 [Global Financial Terminal: AI Stock & Commodity Analyzer (Ultra Speed Edition)](https://global-financial-terminal.streamlit.app/)

A high-performance, real-time financial tracking and AI research terminal built with **Python**, **Streamlit**, **Google Gemini (`gemini-3.8-flash`)**, **yfinance**, **Plotly**, and **Requests**. Designed like an institutional terminal, this app features batched multi-threaded bulk market data fetching, 24×5 futures & exchange session awareness, an interactive in-page AI Analyst popup, fundamental deep dives, news feeds, and embedded live broadcast hubs across major global markets.

[![Live Demo](https://img.shields.io/badge/Streamlit-Live%20Demo-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://global-financial-terminal.streamlit.app/)

---

## 🚀 Key Features

- **⚡ Ultra-Fast Threaded Bulk Fetch Engine**: Downloads 5 days of daily market data for benchmark indices and entire constituent baskets in a single multi-threaded `yf.download()` batch, sorted by volume with `% Change`, `Market Sentiment`, and one-click `AI Agent` triggers.
- **🌍 7 Global Markets & Commodities Coverage**: Instantly switch between 6 major international equity exchanges and global commodity futures:
  - 🇮🇳 **Nifty 50** (`^NSEI`, NSE India)
  - 🇺🇸 **Nasdaq Top 50** (`^NDX`, US Tech & Growth)
  - 🇪🇺 **Euro Stoxx 50** (`^STOXX50E`, European Blue Chips)
  - 🇨🇳 **China Top 50** (`000016.SS`, Shanghai, Shenzhen & HK)
  - 🇯🇵 **Nikkei Top 50** (`^N225`, Tokyo Stock Exchange)
  - 🇰🇷 **KOSPI Top 50** (`^KS11`, Korea Exchange)
  - 🛢️ **Global Commodities** (`DBC`, Energy, Precious/Industrial Metals & Agriculture Futures)
- **⭐ In-Page AI Agent Research Popup**: Click any **⭐** cell in the live table to launch an instant in-page modal report powered by **Gemini 3.8 Flash** (with an automatic quantitative fallback engine):
  - **Quantitative Technical Engine**: Computes live 20/50/200-DMA trends, 14-day RSI, 14-day ATR volatility bands, and 20-day Support & Resistance levels.
  - **Institutional Synthesis**: Combines technicals, fundamentals, and recent Google Finance headlines into an **Executive Summary**, **Key Pros (Bull Case)**, **Key Cons & Risks (Bear Case)**, and an **Actionable Entry, Stop-Loss & Exit Target Plan**.
- **🕒 Smart Market & Futures Session Awareness**: Evaluates local exchange timezones, weekday status, split Asian sessions, and 24×5 CME/COMEX/NYMEX futures trading windows—automatically pausing background polling when markets are closed or while reading an AI report.
- **📊 Concurrent Stock & Commodity Deep Dive**: Click any ticker to load fundamentals, intraday charts, and headlines in parallel:
  - **Valuation & Dividend Metrics**: Trailing & Forward P/E, P/B ratio, EPS, Book Value, Market Cap, Dividend Rate, Yield, and Ex-Dividend Dates.
  - **Interactive Intraday Charts**: Switch between **Line** and **Candlestick** views powered by Plotly.
  - **Live Headlines**: Scrapes Google Finance quote pages with automatic Google News RSS fallback.
- **📺 Index & Live Broadcast Hub**: Open any benchmark index to view index metrics, live YouTube stream embeds (via `UULV` playlist RSS feeds with pooled HTTP sessions), intraday charts, and market news.
- **☀️🌙 Synced Light & Dark Themes (Anti-Ghosting)**: Instant theme switcher that synchronizes custom CSS, Plotly charts, `st.dataframe` canvas cells, and modal dialogs while suppressing rerun fade/ghosting artifacts.
- **🔄 Smart Auto-Refresh Controls**: Configurable auto-refresh interval slider (`5s`–`60s`) with targeted market cache clearing.

---

## 🛠️ Tech Stack

- **Frontend & Framework**: [Streamlit](https://streamlit.io/) (`@st.fragment`, `@st.dialog`, single-cell selection)
- **AI & Quantitative Analysis**: [Google Gen AI SDK](https://ai.google.dev/) (`gemini-3.8-flash` Interactions API) & [Pandas](https://pandas.pydata.org/)
- **Market Data & HTTP Pooling**: [yfinance](https://github.com/ranaroussi/yfinance) & [Requests](https://requests.readthedocs.io/) (`requests.Session`)
- **Interactive Visualization**: [Plotly](https://plotly.com/python/)
- **HTML / RSS Parsing**: [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/) & `xml.etree.ElementTree`

---

## 📁 Project Structure

```text
financial_terminal/
├── app.py                  # Entry point, theme toggle & view router
├── requirements.txt        # Python dependencies
├── README.md               # Project documentation
├── .streamlit/
│   ├── config.toml         # Default Light theme configuration for canvas & modals
│   └── secrets.toml        # GEMINI_API_KEY configuration (not committed to Git)
├── config/
│   ├── __init__.py
│   ├── markets.py          # Equity & commodity symbol lists, 24x5/exchange hours & live channels
│   └── companies.py        # Ticker-to-company & commodity name mapping
├── services/
│   ├── __init__.py
│   ├── ai_agent.py         # RSI/SMA/ATR technical snapshot & Gemini 3.8 Flash AI report generator
│   ├── market_data.py      # Market/futures hours, sentiment, threaded bulk & ticker helpers
│   ├── news.py             # Google Finance scraper with Google News RSS fallback
│   └── live_tv.py          # Pooled HTTP session & YouTube live stream status checks
└── ui/
    ├── __init__.py
    ├── styles.py           # Synced Light/Dark CSS, anti-ghosting rules & dataframe styling
    ├── components.py       # Market status banner, intraday chart & news renderer
    └── views.py            # Main dashboard, in-page AI modal, deep dive & index hub views

```

---

## ⚙️ Installation & Setup

### 1. Prerequisites

Ensure you have **Python 3.10+** installed on your system.

### 2. Clone or Navigate to the Repository

```bash
cd financial_terminal

```

### 3. Install Dependencies

```bash
pip install -U -r requirements.txt

```

### 4. Configure Gemini API Key (Optional for AI Summaries)

Create `.streamlit/secrets.toml` in the project root and add your Google AI Studio API key:

```toml
GEMINI_API_KEY = "your-gemini-api-key-here"

```

*(Note: If no API key is configured, the ⭐ AI Agent automatically falls back to the built-in Quantitative Technical Engine.)*

### 5. Run the App

```bash
streamlit run app.py

```

---

## ⚠️ Disclaimer

Market prices, percentage changes, sentiment tags, news items, live broadcast feeds, and AI-generated technical/fundamental summaries are provided for educational and informational purposes only and do not constitute financial or investment advice.

```

```

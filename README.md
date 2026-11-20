# 🌐 [Global Financial Terminal: AI Stock Analyzer (Ultra Speed Edition)](https://global-financial-terminal.streamlit.app/)

A high-performance, real-time financial tracking dashboard built with **Python**, **Streamlit**, **yfinance**, **Plotly**, and **Requests**. Designed like an institutional terminal, this app features batched bulk market data fetching, market session awareness, fundamental deep dives, news feeds, and embedded live broadcast hubs across major global indices[cite: 2].

[![Live Demo](https://img.shields.io/badge/Streamlit-Live%20Demo-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://global-financial-terminal.streamlit.app/)

---

## 🚀 Key Features

- **⚡ Ultra-Fast Bulk Fetch Engine**: Downloads 2 days of daily market data for benchmark indices and entire constituent baskets in a single batched `yf.download()` call, sorted by volume with `% Change` and `Market Sentiment` classifications[cite: 2].
- **🌍 Multi-Market Coverage**: Instantly switch between 6 major international equity markets[cite: 2]:
  - 🇮🇳 **Nifty 50** (`^NSEI`, NSE India)[cite: 2]
  - 🇺🇸 **Nasdaq Top 50** (`^NDX`, US Tech & Growth)[cite: 2]
  - 🇪🇺 **Euro Stoxx 50** (`^STOXX50E`, European Blue Chips)[cite: 2]
  - 🇨🇳 **China Top 50** (`000016.SS`, Shanghai, Shenzhen & HK)[cite: 2]
  - 🇯🇵 **Nikkei Top 50** (`^N225`, Tokyo Stock Exchange)[cite: 2]
  - 🇰🇷 **KOSPI Top 50** (`^KS11`, Korea Exchange)[cite: 2]
- **🕒 Market Session Status**: Checks local exchange time, weekday status, and trading hours to show whether each market is open or closed[cite: 2].
- **📊 Stock Deep Dive & Analytics**: Click any stock ticker to inspect price action and fundamentals[cite: 2]:
  - Valuation metrics: Trailing & Forward P/E, P/B ratio, EPS, Book Value, and Market Cap[cite: 2].
  - Dividend stats: Dividend Rate, Yield, and Ex-Dividend Dates[cite: 2].
  - Intraday Charts: Switch between **Line** and **Candlestick** views powered by interactive Plotly graphs[cite: 2].
  - Stock Headlines: Fetches recent headlines via Google Finance / Google News RSS[cite: 2].
- **📺 Index & Live Broadcast Hub**: Open any benchmark index to view index metrics, live YouTube stream embeds (using channel `UULV` RSS feeds with concurrent live status checks), intraday charts, and market news[cite: 2].
- **☀️🌙 Light & Dark Terminal Themes**: Instant theme toggle with custom CSS styling for both Light and Dark modes[cite: 2].
- **🔄 Auto-Refresh Controls**: Configurable auto-refresh interval slider (`5s`–`60s`) with a manual refresh & cache-clear button[cite: 2].

---

## 🛠️ Tech Stack

- **Frontend & Framework**: [Streamlit](https://streamlit.io/)
- **Data Retrieval**: [yfinance](https://github.com/ranaroussi/yfinance) & [Requests](https://requests.readthedocs.io/)
- **Data Manipulation**: [Pandas](https://pandas.pydata.org/)
- **Interactive Visualization**: [Plotly](https://plotly.com/python/)
- **HTML / RSS Parsing**: [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/) & `xml.etree.ElementTree`[cite: 2]

---

## 📁 Project Structure

```text
financial_terminal/
├── app.py                  # Entry point, theme toggle & view router
├── requirements.txt        # Python dependencies
├── README.md               # Project documentation
├── config/
│   ├── __init__.py
│   ├── markets.py          # Symbol lists, exchange sessions, indices & live channels
│   └── companies.py        # Ticker-to-company name mapping
├── services/
│   ├── __init__.py
│   ├── market_data.py      # Market hours, sentiment, bulk & ticker yfinance helpers
│   ├── news.py             # Google Finance scraper with Google News RSS fallback
│   └── live_tv.py          # YouTube live stream lookup & concurrent status checks
└── ui/
    ├── __init__.py
    ├── styles.py           # Light/Dark CSS & cell color styling
    ├── components.py       # Market status banner, intraday chart & news renderer
    └── views.py            # Main dashboard, stock deep dive & index hub views

```

---

## ⚙️ Installation & Setup

### 1. Prerequisites

Ensure you have Python 3.9 or higher installed on your system.

### 2. Clone or Download the Repository

Navigate to your project directory:

```bash
cd financial_terminal

```

### 3. Install Dependencies

Install the required Python packages:

```bash
pip install -r requirements.txt

```

### 4. Run the App

Start the Streamlit server:

```bash
streamlit run app.py

```

---

## ⚠️ Disclaimer

Market prices, percentage changes, sentiment tags, news items, and live broadcast feeds are provided for informational purposes only and do not constitute financial or investment advice.


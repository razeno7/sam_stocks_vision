import streamlit as st
import yfinance as yf
import pandas as pd
import requests
import xml.etree.ElementTree as ET

class MarketData:
    def __init__(self, api_key):
        self.api_key = api_key
        # Note: yfinance does not require an API key for market data
        
    @st.cache_data(ttl=600)  # Cache for 10 minutes
    def get_candlestick_data(_self, symbol):
        """Fetches daily data using yfinance."""
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period="1y")
            
            if data.empty:
                return pd.DataFrame()

            data = data.rename(columns={
                'Open': 'Open', 'High': 'High', 'Low': 'Low', 'Close': 'Close', 'Volume': 'Volume',
            })
            
            data.index = pd.to_datetime(data.index)
            if data.index.tz is not None:
                data.index = data.index.tz_localize(None)
                
            return data.sort_index()
        except Exception as e:
            st.error(f"Error fetching data for {symbol}: {e}")
            return pd.DataFrame()

    @st.cache_data(ttl=600)
    def get_rsi(_self, symbol):
        """Calculates RSI (14) locally using yfinance data."""
        try:
            df = _self.get_candlestick_data(symbol)
            if df.empty or len(df) < 15:
                # Fallback to empty df if not enough data
                return pd.DataFrame()
            
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            
            rs = gain / loss
            df['RSI'] = 100 - (100 / (1 + rs))
            return df[['RSI']].dropna()
        except Exception as e:
            return pd.DataFrame()

    @st.cache_data(ttl=600)
    def get_technical_indicators(_self, symbol):
        """Calculates MACD and Bollinger Bands."""
        df = _self.get_candlestick_data(symbol)
        if df.empty: return pd.DataFrame()
        
        # MACD
        df['EMA12'] = df['Close'].ewm(span=12, adjust=False).mean()
        df['EMA26'] = df['Close'].ewm(span=26, adjust=False).mean()
        df['MACD'] = df['EMA12'] - df['EMA26']
        df['Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
        
        # Bollinger Bands
        df['SMA20'] = df['Close'].rolling(window=20).mean()
        df['STD20'] = df['Close'].rolling(window=20).std()
        df['BB_Upper'] = df['SMA20'] + (df['STD20'] * 2)
        df['BB_Lower'] = df['SMA20'] - (df['STD20'] * 2)
        
        return df.tail(100)

    @st.cache_data(ttl=3600) # Cache info for 1 hour
    def get_company_info(_self, symbol):
        """Fetches company profile data."""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            # Safe extraction with defaults
            def format_large_num(num):
                if not isinstance(num, (int, float)): return "N/A"
                if num >= 1e12: return f"{num/1e12:.2f}T"
                if num >= 1e9: return f"{num/1e9:.2f}B"
                if num >= 1e6: return f"{num/1e6:.2f}M"
                return f"{num:.2f}"

            # Fallback to fast_info for critical metrics if info fails
            fast = ticker.fast_info
            
            def get_val(key, fast_key=None, default="N/A"):
                val = info.get(key)
                if val: return val
                if fast_key and hasattr(fast, fast_key):
                    return fast[fast_key]
                return default

            mkt_cap = format_large_num(get_val("marketCap", "market_cap", 0))
            high_52 = get_val("fiftyTwoWeekHigh", "year_high", "N/A")
            low_52 = get_val("fiftyTwoWeekLow", "year_low", "N/A")
            
            # Format high/low if they are numbers
            if isinstance(high_52, (int, float)): high_52 = f"{high_52:.2f}"
            if isinstance(low_52, (int, float)): low_52 = f"{low_52:.2f}"

            return {
                "name": info.get("shortName", symbol),
                "sector": info.get("sector", "Unknown"),
                "industry": info.get("industry", "Unknown"),
                "marketCap": mkt_cap,
                "peRatio": f"{info.get('trailingPE', 0):.2f}",
                "beta": f"{info.get('beta', 0):.2f}",
                "dividend": f"{info.get('dividendYield', 0)*100:.2f}%" if info.get('dividendYield') else "N/A",
                "high52": high_52,
                "low52": low_52,
                "summary": info.get("longBusinessSummary", "No summary available.")
            }
        except Exception:
            return {}



    def _get_google_news(self, symbol):
        """Fallback: Fetch news from Google News RSS."""
        try:
            url = f"https://news.google.com/rss/search?q={symbol}+stock&hl=en-US&gl=US&ceid=US:en"
            r = requests.get(url, timeout=5)
            root = ET.fromstring(r.text)
            
            news_items = []
            for item in root.findall('./channel/item')[:5]:
                title = item.find('title').text
                link = item.find('link').text
                pubDate = item.find('pubDate').text
                
                news_items.append({
                    "title": title,
                    "summary": f"Published: {pubDate}", 
                    "overall_sentiment_label": "Unknown",
                    "url": link
                })
            return news_items
        except Exception as e:
            # st.warning(f"Google News Fallback Failed: {e}")
            return []

    @st.cache_data(ttl=900)
    def get_news_sentiment(_self, symbol):
        """
        Fetches news from yfinance, falls back to Google News RSS if needed.
        """
        news_items = []
        
        # 1. Try yfinance
        try:
            ticker = yf.Ticker(symbol)
            yf_news = ticker.news
            for item in yf_news:
                title = item.get("title")
                publisher = item.get("publisher", "Unknown") 
                link = item.get("link", "")
                
                if not title or title == "No Headline": 
                    continue
                
                news_items.append({
                    "title": title,
                    "summary": f"Source: {publisher}",
                    "overall_sentiment_label": "Unknown",
                    "url": link
                })
        except Exception:
            pass
            
        # 2. Fallback to Google News if yfinance gave weak results
        if len(news_items) < 2:
            google_news = _self._get_google_news(symbol)
            if google_news:
                return google_news
        
        return news_items[:5]

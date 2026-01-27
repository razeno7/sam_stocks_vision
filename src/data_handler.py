import streamlit as st
import yfinance as yf
import pandas as pd
import requests

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

            return {
                "name": info.get("shortName", symbol),
                "sector": info.get("sector", "Unknown"),
                "industry": info.get("industry", "Unknown"),
                "marketCap": format_large_num(info.get("marketCap", 0)),
                "peRatio": f"{info.get('trailingPE', 0):.2f}",
                "beta": f"{info.get('beta', 0):.2f}",
                "dividend": f"{info.get('dividendYield', 0)*100:.2f}%" if info.get('dividendYield') else "N/A",
                "summary": info.get("longBusinessSummary", "No summary available.")
            }
        except Exception:
            return {}

    @st.cache_data(ttl=900)
    def get_news_sentiment(_self, symbol):
        """
        Fetches news from yfinance to avoid Alpha Vantage rate limits.
        """
        try:
            ticker = yf.Ticker(symbol)
            news = ticker.news
            formatted_news = []
            for item in news:
                title = item.get("title", "No Headline")
                publisher = item.get("publisher", "Source Unknown") 
                link = item.get("link", "")
                
                # yfinance sometimes returns UUIDs as titles or None
                if not title: title = "Market Update"
                
                formatted_news.append({
                    "title": title,
                    "summary": f"{publisher}",
                    "overall_sentiment_label": "Unknown",
                    "url": link
                })
            return formatted_news[:5]
        except Exception as e:
            return []

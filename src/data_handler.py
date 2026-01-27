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
            # yfinance tickers for futures often have =F, e.g., GC=F for Gold.
            # We try the symbol as is.
            ticker = yf.Ticker(symbol)
            # Fetch 1 year of data to ensure enough for RSI and charts
            data = ticker.history(period="1y")
            
            if data.empty:
                return pd.DataFrame()

            # Ensure columns are Title Case (Open, High, Low, Close, Volume)
            # yfinance usually returns Title Case by default or proper case.
            # Standardize just in case.
            data = data.rename(columns={
                'Open': 'Open',
                'High': 'High',
                'Low': 'Low',
                'Close': 'Close',
                'Volume': 'Volume',
            })
            
            # Ensure index is datetime
            data.index = pd.to_datetime(data.index)
            # Remove timezone info if present for cleaner display
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
                return pd.DataFrame()
            
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            
            rs = gain / loss
            df['RSI'] = 100 - (100 / (1 + rs))
            
            # Return last rows mainly, or full df
            return df[['RSI']].dropna()
        except Exception as e:
            st.warning(f"Error calculating RSI for {symbol}: {e}")
            return pd.DataFrame()

    @st.cache_data(ttl=900)  # Cache news for 15 minutes
    def get_news_sentiment(_self, symbol):
        """
        Fetches news sentiment from Alpha Vantage.
        Returns a list of news items (dictionaries).
        """
        # Alpha Vantage News is still one of the best free sources for structured sentiment.
        url = f"https://www.alphavantage.co/query?function=NEWS_SENTIMENT&tickers={symbol}&sort=LATEST&limit=5&apikey={_self.api_key}"
        try:
            r = requests.get(url)
            data = r.json()
            if "feed" in data:
                return data["feed"]
            else:
                # Fallback or error handling
                if "Information" in data:
                    st.warning(f"Alpha Vantage Limit: {data['Information']}")
                return []
        except Exception as e:
            st.error(f"Error fetching news for {symbol}: {e}")
            return []

import streamlit as st
from alpha_vantage.timeseries import TimeSeries
from alpha_vantage.techindicators import TechIndicators
import pandas as pd
import requests

class MarketData:
    def __init__(self, api_key):
        self.api_key = api_key
        self.ts = TimeSeries(key=api_key, output_format='pandas')
        self.ti = TechIndicators(key=api_key, output_format='pandas')

    @st.cache_data(ttl=600)  # Cache for 10 minutes
    def get_candlestick_data(_self, symbol):
        """Fetches daily adjusted close data."""
        try:
            data, meta_data = _self.ts.get_daily_adjusted(symbol=symbol)
            # Rename columns for convenience/Plotly
            data = data.rename(columns={
                '1. open': 'Open',
                '2. high': 'High',
                '3. low': 'Low',
                '4. close': 'Close',
                '5. adjusted close': 'Adj Close',
                '6. volume': 'Volume'
            })
            data.index = pd.to_datetime(data.index)
            return data.sort_index()
        except Exception as e:
            st.error(f"Error fetching data for {symbol}: {e}")
            return pd.DataFrame()

    @st.cache_data(ttl=600)
    def get_rsi(_self, symbol):
        """Fetches RSI indicator."""
        try:
            data, meta_data = _self.ti.get_rsi(symbol=symbol)
            return data
        except Exception as e:
            st.warning(f"Error fetching RSI for {symbol}: {e}")
            return pd.DataFrame()

    @st.cache_data(ttl=900)  # Cache news for 15 minutes
    def get_news_sentiment(_self, symbol):
        """
        Fetches news sentiment from Alpha Vantage.
        Returns a list of news items (dictionaries).
        """
        url = f"https://www.alphavantage.co/query?function=NEWS_SENTIMENT&tickers={symbol}&sort=LATEST&limit=5&apikey={_self.api_key}"
        try:
            r = requests.get(url)
            data = r.json()
            if "feed" in data:
                return data["feed"]
            else:
                return []
        except Exception as e:
            st.error(f"Error fetching news for {symbol}: {e}")
            return []

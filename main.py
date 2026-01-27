import streamlit as st
import plotly.graph_objects as go
from src.ui_components import apply_terminal_theme, display_header, display_news_card
from src.data_handler import MarketData
from src.ai_insights import GeminiAnalyst

# 1. Page Config
st.set_page_config(
    page_title="Sam Stocks Vision",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Apply Theme
apply_terminal_theme()

# 3. Sidebar & Configuration
st.sidebar.title("SETTINGS")

# Check for secrets or ask user
if "api_keys" in st.secrets:
    av_key = st.secrets["api_keys"].get("alpha_vantage", "")
    gemini_key = st.secrets["api_keys"].get("gemini", "")
else:
    av_key = st.sidebar.text_input("Alpha Vantage Key", type="password")
    gemini_key = st.sidebar.text_input("Gemini API Key", type="password")

symbol = st.sidebar.text_input("SYMBOL", value="GOOGL").upper()

if not av_key or not gemini_key:
    st.warning("Please provide both Alpha Vantage and Gemini API keys to proceed.")
    st.stop()

# 4. Initialize Modules
market_data = MarketData(av_key)
analyst = GeminiAnalyst(gemini_key)

# 5. Main Layout
display_header(f"MARKET ANALYSIS: {symbol}")

col1, col2, col3 = st.columns([2, 1, 1])

# --- Column 1: Chart ---
with col1:
    st.subheader("PRICE ACTION")
    with st.spinner("Fetching Market Data..."):
        df = market_data.get_candlestick_data(symbol)
        
        if not df.empty:
            fig = go.Figure(data=[go.Candlestick(
                x=df.index,
                open=df['Open'],
                high=df['High'],
                low=df['Low'],
                close=df['Close'],
                increasing_line_color='#00FF41', 
                decreasing_line_color='#FF0000'
            )])
            
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#00FF41', family='Courier New'),
                xaxis_rangeslider_visible=False,
                margin=dict(l=0, r=0, t=0, b=0)
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No market data available.")

# --- Column 2: Sentiment Indicators ---
with col2:
    st.subheader("INDICATORS")
    with st.spinner("Calculating RSI..."):
        rsi_df = market_data.get_rsi(symbol)
        if not rsi_df.empty:
            last_rsi = rsi_df.iloc[-1]['RSI']
            st.metric("RSI (14)", f"{last_rsi:.2f}")
            
            # Simple Gauge (using Plotly Indicator)
            fig_gauge = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = last_rsi,
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': "RSI Momentum"},
                gauge = {
                    'axis': {'range': [0, 100], 'tickcolor': "#00FF41"},
                    'bar': {'color': "#00FF41"},
                    'bgcolor': "#000000",
                    'borderwidth': 2,
                    'bordercolor': "#333",
                    'steps': [
                        {'range': [0, 30], 'color': '#004411'},
                        {'range': [30, 70], 'color': '#002200'},
                        {'range': [70, 100], 'color': '#440000'} # Overbought
                    ],
                }
            ))
            fig_gauge.update_layout(
                paper_bgcolor='rgba(0,0,0,0)', 
                font=dict(color='#00FF41', family='Courier New'),
                margin=dict(l=20, r=20, t=30, b=20),
                height=200
            )
            st.plotly_chart(fig_gauge, use_container_width=True)

# --- Column 3: AI Insights ---
with col3:
    st.subheader("AI INTELLIGENCE")
    with st.spinner("Analyzing News..."):
        news = market_data.get_news_sentiment(symbol)
        if news:
            analysis_text = analyst.analyze_news(symbol, news)
            
            # Simple parsing for display (or just dump text)
            st.markdown(f"```\n{analysis_text}\n```")
            
            st.write("---")
            st.caption("LATEST HEADLINES")
            for item in news[:3]: # Show top 3 headlines
                sentiment_label = item.get('overall_sentiment_label', 'Neutral')
                display_news_card(item.get('title'), item.get('summary')[:100]+"...", sentiment_label)
        else:
            st.info("No recent news found.")

import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from src.ui_components import apply_terminal_theme, display_header, display_news_card
from src.data_handler import MarketData
from src.ai_insights import GeminiAnalyst

# 1. Page Config
st.set_page_config(
    page_title="SAM STOCKS VISION",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="⚡"
)

# 2. Apply Theme
apply_terminal_theme()

# 3. Sidebar
st.sidebar.markdown("""
<div style="text-align: center; margin-bottom: 20px;">
    <h1 style="color: #00FF41; font-size: 2em; margin: 0; padding: 0;">SAM</h1>
    <h1 style="color: #e0e0e0; font-size: 1.5em; margin: 0; padding: 0;">STOCKS VISION</h1>
    <div style="height: 2px; background: #00FF41; margin-top: 10px; box-shadow: 0 0 10px #00FF41;"></div>
</div>
""", unsafe_allow_html=True)

# Secrets handling
if "api_keys" in st.secrets:
    av_key = st.secrets["api_keys"].get("alpha_vantage", "")
    gemini_key = st.secrets["api_keys"].get("gemini", "")
else:
    av_key = st.sidebar.text_input("Alpha Vantage Key", type="password")
    gemini_key = st.sidebar.text_input("Gemini API Key", type="password")

symbol = st.sidebar.text_input("QUERY TICKER", value="NVDA").upper().strip()

if not av_key or not gemini_key:
    st.sidebar.warning("SYSTEM LOCKED: MISSING KEYS")
    st.stop()

# 4. Initialize Modules
market_data = MarketData(av_key)
analyst = GeminiAnalyst(gemini_key)

# 5. Header & Company Info
col_title, col_info = st.columns([1, 2])
with col_title:
    st.markdown(f"<h1 style='font-size: 3rem; color: #00FF41; margin-bottom: 0;'>{symbol}</h1>", unsafe_allow_html=True)
with col_info:
    info = market_data.get_company_info(symbol)
    if info:
        st.markdown(f"""
        <div style="display: flex; gap: 20px; align-items: center; border: 1px solid #333; padding: 10px; background: #0a0a0a;">
            <div><span style="color:#666">SECTOR</span><br><span style="color:#e0e0e0">{info.get('sector')}</span></div>
            <div><span style="color:#666">MKT CAP</span><br><span style="color:#00FF41">{info.get('marketCap')}</span></div>
            <div><span style="color:#666">P/E</span><br><span style="color:#FFB000">{info.get('peRatio')}</span></div>
            <div><span style="color:#666">BETA</span><br><span style="color:#e0e0e0">{info.get('beta')}</span></div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")

# 6. Main Tabs
tab1, tab2, tab3 = st.tabs(["MARKET OVERVIEW", "TECHNICAL DEEP DIVE", "INTELLIGENCE LAYER"])

with tab1:
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### PRICE ACTION")
        df = market_data.get_candlestick_data(symbol)
        if not df.empty:
            fig = go.Figure(data=[go.Candlestick(
                x=df.index,
                open=df['Open'], high=df['High'],
                low=df['Low'], close=df['Close'],
                increasing_line_color='#00FF41', 
                decreasing_line_color='#FF0000'
            )])
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#e0e0e0', family='Share Tech Mono'),
                xaxis_rangeslider_visible=False,
                margin=dict(l=0, r=0, t=10, b=0),
                height=350, # Reduced height
                yaxis=dict(gridcolor='#111'),
                xaxis=dict(gridcolor='#111')
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.error("DATA FEED UNAVAILABLE")

    with col2:
        st.markdown("### MOMENTUM")
        rsi_df = market_data.get_rsi(symbol)
        if not rsi_df.empty:
            last_rsi = rsi_df.iloc[-1]['RSI']
            fig_gauge = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = last_rsi,
                gauge = {
                    'axis': {'range': [0, 100], 'tickcolor': "#00FF41"},
                    'bar': {'color': "#00FF41"},
                    'bgcolor': "#000000",
                    'borderwidth': 2,
                    'bordercolor': "#333",
                    'steps': [
                        {'range': [0, 30], 'color': '#004411'},
                        {'range': [70, 100], 'color': '#440000'}
                    ],
                }
            ))
            fig_gauge.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#00FF41'),
                margin=dict(l=20, r=20, t=20, b=20),
                height=250
            )
            st.plotly_chart(fig_gauge, use_container_width=True)
            
            # Additional small metrics underneath
            st.markdown(f"""
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
                <div style="border: 1px solid #333; padding: 5px; text-align: center;">
                    <div style="color: #666; font-size: 0.8em;">52W HIGH</div>
                    <div style="color: #00FF41;">{info.get('high52', 'N/A')}</div>
                </div>
                <div style="border: 1px solid #333; padding: 5px; text-align: center;">
                    <div style="color: #666; font-size: 0.8em;">52W LOW</div>
                    <div style="color: #FF0000;">{info.get('low52', 'N/A')}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)


with tab2:
    st.markdown("### ADVANCED METRICS (MACD / BOLLINGER)")
    tech_df = market_data.get_technical_indicators(symbol)
    if not tech_df.empty:
        fig_macd = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.7, 0.3], vertical_spacing=0.05)
        
        # Upper: Price + BB
        fig_macd.add_trace(go.Scatter(x=tech_df.index, y=tech_df['Close'], name='Px', line=dict(color='#00FF41', width=1)), row=1, col=1)
        fig_macd.add_trace(go.Scatter(x=tech_df.index, y=tech_df['BB_Upper'], name='BB+', line=dict(color='#333', dash='dot')), row=1, col=1)
        fig_macd.add_trace(go.Scatter(x=tech_df.index, y=tech_df['BB_Lower'], name='BB-', line=dict(color='#333', dash='dot')), row=1, col=1)
        
        # Lower: MACD
        fig_macd.add_trace(go.Scatter(x=tech_df.index, y=tech_df['MACD'], name='MACD', line=dict(color='cyan', width=1)), row=2, col=1)
        fig_macd.add_trace(go.Scatter(x=tech_df.index, y=tech_df['Signal'], name='Sig', line=dict(color='orange', width=1)), row=2, col=1)
        
        fig_macd.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#e0e0e0', family='Share Tech Mono'),
            height=500,
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor='#111'),
            yaxis2=dict(showgrid=True, gridcolor='#111'),
            showlegend=False
        )
        st.plotly_chart(fig_macd, use_container_width=True)

with tab3:
    st.markdown("### NEURAL NETWORK ANALYSIS")
    with st.spinner("Decrypting News Signals..."):
        news = market_data.get_news_sentiment(symbol)
        
        col_ai, col_news = st.columns([1, 1])
        with col_ai:
            st.markdown("<div style='border: 1px solid #00FF41; padding: 15px; margin-bottom: 20px;'>", unsafe_allow_html=True)
            st.markdown("#### > LOG: AI_SYNTHESIS")
            analysis_text = analyst.analyze_news(symbol, news)
            
            # Simple color coding for output
            color = "#e0e0e0"
            if "SENTIMENT_SCORE" in analysis_text:
                st.code(analysis_text, language="yaml")
            else:
                st.warning(analysis_text)
            st.markdown("</div>", unsafe_allow_html=True)
        
        with col_news:
            st.markdown("#### > INCOMING STREAM")
            if news:
                for item in news:
                     display_news_card(item.get('title'), item.get('summary')[:100]+"...", "Neutral")
            else:
                st.caption("No Signal Detected.")

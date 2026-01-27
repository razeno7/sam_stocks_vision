import streamlit as st

def apply_terminal_theme():
    """
    Applies a futuristic Bloomberg-style theme.
    """
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&display=swap');

        /* RESET & BASE */
        .stApp {
            background-color: #050505;
            color: #e0e0e0;
            font-family: 'Share Tech Mono', monospace;
        }

        /* HEADER REMOVAL */
        header {visibility: hidden;}
        .stDeployButton {display:none;}
        footer {visibility: hidden;}

        /* SIDEBAR */
        [data-testid="stSidebar"] {
            background-color: #0a0a0a;
            border-right: 1px solid #1f1f1f;
        }
        [data-testid="stSidebar"] hr {
            border-color: #333;
        }

        /* TEXT STYLES */
        h1, h2, h3 {
            color: #ffb000 !important; /* Amber for headers */
            text-transform: uppercase;
            letter-spacing: 1px;
            font-weight: normal;
        }
        
        .big-font {
            font-size: 24px !important;
            color: #00ff41; /* Neon Green */
        }
        
        /* INPUT FIELDS */
        .stTextInput input {
            background-color: #000;
            border: 1px solid #333;
            color: #00ff41;
            font-family: 'Share Tech Mono', monospace;
            border-radius: 0px;
        }
        .stTextInput input:focus {
            border-color: #ffb000;
            box-shadow: 0 0 5px #ffb000; /* Amber Glow */
        }

        /* METRICS & CARDS */
        div[data-testid="metric-container"] {
            background-color: #0f0f0f;
            border: 1px solid #333;
            padding: 10px;
            border-radius: 0px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.5);
        }
        [data-testid="stMetricLabel"] {
            color: #888 !important;
            font-size: 0.8rem;
        }
        [data-testid="stMetricValue"] {
            color: #00ff41 !important;
            font-family: 'Share Tech Mono', monospace;
        }

        /* NEWS CARD */
        .news-card {
            border-left: 3px solid #333;
            background: #0b0b0b;
            padding: 10px;
            margin-bottom: 8px;
            transition: all 0.2s;
        }
        .news-card:hover {
            background: #111;
            border-left-color: #ffb000;
        }
        .news-title {
            color: #ddd;
            font-weight: bold;
            font-size: 0.95rem;
        }
        .news-meta {
            color: #666;
            font-size: 0.75rem;
            margin-top: 4px;
        }
        .sentiment-Bullish { border-left-color: #00ff41 !important; }
        .sentiment-Bearish { border-left-color: #ff0000 !important; }
        
        /* PLOTLY FIXES */
        .js-plotly-plot .plotly .main-svg {
            background: rgba(0,0,0,0) !important;
        }
        
        </style>
    """, unsafe_allow_html=True)

def display_header(text):
    st.markdown(f"<h2 style='border-bottom: 1px solid #333; padding-bottom: 5px; margin-bottom: 20px;'>{text}</h2>", unsafe_allow_html=True)

def display_news_card(title, summary, sentiment):
    sentiment_class = f"sentiment-{sentiment}"
    st.markdown(f"""
    <div class="news-card {sentiment_class}">
        <div class="news-title">{title}</div>
        <div class="news-meta">[{sentiment.upper()}] | {summary}</div>
    </div>
    """, unsafe_allow_html=True)

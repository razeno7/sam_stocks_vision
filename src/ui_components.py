import streamlit as st

def apply_terminal_theme():
    """
    Applies a custom CSS to mimic a Bloomberg Terminal style.
    Colors: Black background, Neon Green/Amber text, Monospace fonts.
    """
    st.markdown("""
        <style>
        /* Main Background */
        .stApp {
            background-color: #000000;
            color: #00FF41; /* Neon Green */
            font-family: 'Courier New', Courier, monospace;
        }

        /* Sidebar */
        [data-testid="stSidebar"] {
            background-color: #0f0f0f;
            border-right: 1px solid #333;
        }

        /* Text Colors */
        h1, h2, h3, h4, h5, h6, p, label, .stMarkdown {
            color: #00FF41 !important;
            font-family: 'Courier New', Courier, monospace !important;
        }
        
        /* Secondary Text (Amber) */
        .highlight-amber {
            color: #FFB000 !important;
        }

        /* Input Fields */
        .stTextInput input {
            background-color: #1a1a1a;
            color: #00FF41;
            border: 1px solid #333;
            font-family: 'Courier New', Courier, monospace;
        }
        .stTextInput input:focus {
            border-color: #00FF41;
        }

        /* Buttons */
        .stButton button {
            background-color: #1a1a1a;
            color: #00FF41;
            border: 1px solid #00FF41;
            font-family: 'Courier New', Courier, monospace;
            text-transform: uppercase;
        }
        .stButton button:hover {
            background-color: #00FF41;
            color: #000000;
        }
        
        /* Metrics */
        [data-testid="stMetricValue"] {
            color: #00FF41 !important;
            font-family: 'Courier New', Courier, monospace !important;
        }
        
        /* Plotly Chart Background */
        .js-plotly-plot .plotly .main-svg {
            background: rgba(0,0,0,0) !important;
        }
        
        </style>
    """, unsafe_allow_html=True)

def display_header(text):
    """Displays a header in terminal style."""
    st.markdown(f"### > {text}")

def display_news_card(title, summary, sentiment):
    """
    Displays a news item with a sentiment indicator.
    """
    color = "#00FF41" if sentiment == "Bullish" else "#FF0000" if sentiment == "Bearish" else "#FFB000"
    
    st.markdown(f"""
    <div style="border: 1px solid #333; padding: 10px; margin-bottom: 10px; background-color: #0a0a0a;">
        <div style="color: {color}; font-weight: bold; border-bottom: 1px solid #333; padding-bottom: 5px;">
            [{sentiment.upper()}]
        </div>
        <div style="margin-top: 5px; color: #fff;">
            {title}
        </div>
        <div style="margin-top: 5px; font-size: 0.9em; color: #aaa;">
            {summary}
        </div>
    </div>
    """, unsafe_allow_html=True)

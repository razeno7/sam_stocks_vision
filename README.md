# Sam Stocks Vision

A "Bloomberg Terminal" style trading dashboard built with Python and Streamlit.

## Features
- **Real-time Market Data**: Alpha Vantage integration for candlesticks and RSI.
- **AI Insights**: Gemini 1.5 Flash analysis of financial news.
- **Terminal UI**: High-contrast dark mode with neon accents.

## Setup

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run Application**:
   ```bash
   streamlit run main.py
   ```

## API Keys
This project requires API keys for:
- [Alpha Vantage](https://www.alphavantage.co/)
- [Google Gemini](https://ai.google.dev/)

Add them to `.streamlit/secrets.toml` (see `secrets_template.toml`).

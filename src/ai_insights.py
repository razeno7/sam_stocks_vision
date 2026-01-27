import google.generativeai as genai
import streamlit as st

class GeminiAnalyst:
    def __init__(self, api_key):
        if not api_key:
            st.error("Gemini API Key is missing.")
            return
        genai.configure(api_key=api_key)
        self.model = self._get_best_model()

    def _get_best_model(self):
        """
        Iterates through known model names to find one that works.
        """
        candidates = [
            'gemini-1.5-flash',
            'gemini-1.5-flash-latest',
            'gemini-1.5-pro',
            'gemini-1.5-pro-latest',
            'gemini-1.0-pro',
            'gemini-pro'
        ]
        
        # Method 1: Try to look for them in list_models (most reliable)
        try:
            available_models = [m.name.replace('models/', '') for m in genai.list_models()]
            for candle in candidates:
                if candle in available_models:
                    return genai.GenerativeModel(candle)
        except Exception as e:
            print(f"List models failed: {e}")

        # Method 2: Blind trial (fallback)
        # We return the most likely to work: 1.5 Flash
        return genai.GenerativeModel('gemini-1.5-flash')

    def analyze_news(self, ticker, news_items):
        """
        Uses Gemini to summarize news and determine sentiment.
        """
        if not news_items:
            return "No news available for analysis.", "Neutral"

        # Prepare context for the LLM
        news_text = ""
        for item in news_items:
            title = item.get('title', 'No Title')
            summary = item.get('summary', 'No Summary')
            news_text += f"- {title}: {summary}\n"

        prompt = f"""
        You are a senior financial analyst acting as a signal generator for a high-frequency trading terminal. 
        Analyze the following news for {ticker}.
        
        News Data:
        {news_text}
        
        Directives:
        1. Synthesize the news into a single, dense paragraph of max 50 words. Focus on hard data and market impact.
        2. Assign a sentiment score from -100 (Bearish) to +100 (Bullish).
        
        Output format:
        SENTIMENT_SCORE: [Number]
        SUMMARY: [Text]
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            # st.error(f"Error generating AI insights: {e}")
            return f"AI Analysis Unavailable: {str(e)[:100]}...", "Unknown"

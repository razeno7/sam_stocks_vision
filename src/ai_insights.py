import google.generativeai as genai
import streamlit as st
import time

class GeminiAnalyst:
    def __init__(self, api_key):
        if not api_key:
            st.error("Gemini API Key is missing.")
            return
        genai.configure(api_key=api_key)
    def _try_generate(self, model_name, prompt):
        """Attempts to generate content with a specific model."""
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            return response.text, None
        except Exception as e:
            return None, str(e)

    def analyze_news(self, ticker, news_items):
        """
        Uses Gemini to summarize news with multi-model fallback.
        """
        if not news_items:
            return "No news available for analysis.", "Neutral"

        # Prepare context
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
        1. Synthesize the news into a single, dense paragraph of max 30 words. Focus on hard data and market impact.
        2. Assign a sentiment score from -100 (Bearish) to +100 (Bullish).
        
        Output format:
        SENTIMENT_SCORE: [Number]
        SUMMARY: [Text]
        """
        
        # Candidate models - Prioritize exact matches from debug output
        candidates = [
            'models/gemini-2.5-flash',
            'models/gemini-2.0-flash',
            'models/gemini-1.5-flash', 
            'gemini-2.0-flash',
            'gemini-1.5-flash'
        ]
        
        errors = []
        for model_name in candidates:
            result, error = self._try_generate(model_name, prompt)
            if result:
                return result
            if error:
                errors.append(f"{model_name}: {error}")
        
        # If all failed, give detailed debug info
        try:
            available = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            debug_msg = f"ALL ATTEMPTS FAILED. Errors: {' | '.join(errors)} | CONST_AVAILABLE: {', '.join(available)}"
        except Exception as e:
            debug_msg = f"Could not list models: {e}. Last error: {errors[-1] if errors else 'None'}"

        return f"AI Generation Failed. {debug_msg} \n\n(Try refreshing permissions or checking API key quotas.)", "Unknown"

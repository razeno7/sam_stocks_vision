import google.generativeai as genai
import streamlit as st

class GeminiAnalyst:
    def __init__(self, api_key):
        if not api_key:
            st.error("Gemini API Key is missing.")
            return
        genai.configure(api_key=api_key)
        # Try to use the latest Flash model, fallback will be handled by exception if needed
        # Switching to gemini-pro as it is the most stable and widely available model
        self.model = genai.GenerativeModel('gemini-pro')

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
        You are a senior financial analyst. Analyze the following recent news for {ticker}.
        
        News:
        {news_text}
        
        Task:
        1. Provide a concise summary (max 3 bullet points).
        2. Determine the overall short-term sentiment based ONLY on these news items.
        
        Format your response exactly as:
        SENTIMENT: [BULLISH/BEARISH/NEUTRAL]
        SUMMARY:
        - [Point 1]
        - [Point 2]
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            st.error(f"Error generating AI insights: {e}")
            return "Error generating analysis.", "Unknown"

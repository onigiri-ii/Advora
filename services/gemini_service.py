import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

class GeminiService:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("Missing Gemini API key")
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-pro')
    
    def analyze_patterns(self, entries):
        """Analyze symptom patterns from entries"""
        prompt = f"""
        Analyze these symptom entries and provide insights:
        
        {entries}
        
        Please provide:
        1. Key patterns observed
        2. Correlations with period/stress
        3. Red flags if any
        4. Summary for doctor discussion
        """
        
        response = self.model.generate_content(prompt)
        return response.text
    
    def generate_daily_summary(self, entry):
        """Generate summary for a single entry"""
        prompt = f"""
        Provide a brief, empathetic summary of this symptom entry:
        
        {entry}
        """
        
        response = self.model.generate_content(prompt)
        return response.text
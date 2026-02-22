import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

class GeminiService:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("Missing Gemini API key")
        
        # Initialize the new client
        self.client = genai.Client(api_key=self.api_key)
        # Use the latest model name
        self.model_name = "gemini-2.5-flash-lite"  # or "gemini-1.5-pro" for more complex tasks
        print(f"✅ Gemini client initialized with model: {self.model_name}")
    
    def analyze_patterns(self, entries):
        """Analyze symptom patterns from entries"""
        try:
            prompt = f"""
            Analyze these symptom entries and provide insights:
            
            {entries}
            
            Please provide:
            1. Key patterns observed
            2. Correlations with period/stress
            3. Red flags if any
            4. Summary for doctor discussion
            """
            
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            return response.text
            
        except Exception as e:
            print(f"Gemini API Error: {e}")
            return "⚠️ Unable to generate insights at this moment. Please try again later."
    
    def generate_daily_summary(self, entry):
        """Generate summary for a single entry"""
        try:
            prompt = f"""
            Provide a brief, empathetic summary of this symptom entry:
            
            {entry}
            """
            
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            return response.text
            
        except Exception as e:
            print(f"Gemini API Error: {e}")
            return "Summary unavailable at this time."
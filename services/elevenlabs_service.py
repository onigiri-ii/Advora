import os
from dotenv import load_dotenv

load_dotenv()

class ElevenLabsService:
    def __init__(self):
        self.api_key = os.getenv("ELEVENLABS_API_KEY", "mock_key")
        print("⚠️ ElevenLabs service initialized in MOCK mode")
    
    def transcribe_audio(self, audio_base64):
        """Mock transcription for testing"""
        return "I have a headache and feel tired today. My cramps are bad."
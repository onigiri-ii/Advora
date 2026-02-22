import os
import requests
import base64
from dotenv import load_dotenv

load_dotenv()

class ElevenLabsService:
    def __init__(self):
        self.api_key = os.getenv("ELEVENLABS_API_KEY")
        if not self.api_key:
            raise ValueError("Missing ElevenLabs API key")
        self.base_url = "https://api.elevenlabs.io/v1"
        print(f"✅ ElevenLabs service initialized with key starting: {self.api_key[:8]}...")
    
    def transcribe_audio(self, audio_base64):
        """
        Convert speech to text using ElevenLabs Speech-to-Text
        Sends audio as a file upload (multipart/form-data)
        """
        if not audio_base64:
            print("❌ No audio data provided")
            return None
        
        # Decode base64 to bytes
        try:
            audio_bytes = base64.b64decode(audio_base64)
            print(f"✅ Audio decoded: {len(audio_bytes)} bytes")
        except Exception as e:
            print(f"❌ Failed to decode audio: {e}")
            return None
        
        # Prepare headers
        headers = {
            "xi-api-key": self.api_key
        }
        
        # Prepare the audio file for upload
        files = {
            'file': ('audio.webm', audio_bytes, 'audio/webm')
        }
        
        # Optional parameters
        data = {
            'model_id': 'scribe_v1'
        }
        
        try:
            print("📤 Sending request to ElevenLabs STT...")
            response = requests.post(
                f"{self.base_url}/speech-to-text",
                headers=headers,
                files=files,
                data=data,
                timeout=30
            )
            
            print(f"📥 Response status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                transcript = result.get("text", "")
                print(f"✅ Transcription successful: {transcript[:50]}...")
                return transcript
            else:
                print(f"❌ ElevenLabs API error: {response.status_code}")
                print(f"Response body: {response.text}")
                return None
                
        except requests.exceptions.Timeout:
            print("❌ Request timed out")
            return None
        except Exception as e:
            print(f"❌ Error calling ElevenLabs: {e}")
            return None
import os
import requests
import base64
from dotenv import load_dotenv

load_dotenv()

def test_elevenlabs_speech_to_text():
    api_key = os.getenv("ELEVENLABS_API_KEY")
    print(f"API Key exists: {'Yes' if api_key else 'No'}")
    print(f"API Key starts with: {api_key[:8] if api_key else 'None'}...")
    
    if not api_key:
        print("❌ No ElevenLabs API key found in .env")
        return
    
    # First, test text-to-speech (more reliable endpoint to check if API works)
    print("\n1. Testing text-to-speech (to verify API key)...")
    headers = {
        "xi-api-key": api_key,
        "Content-Type": "application/json"
    }
    
    tts_data = {
        "text": "Hello, this is a test.",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.5
        }
    }
    
    try:
        response = requests.post(
            "https://api.elevenlabs.io/v1/text-to-speech/21m00Tcm4TlvDq8ikWAM",  # Rachel voice
            headers=headers,
            json=tts_data
        )
        
        if response.status_code == 200:
            print("✅ Text-to-speech works! API key is valid.")
        else:
            print(f"❌ Text-to-speech failed: {response.status_code}")
            print(f"Response: {response.text}")
            
            # Check if it's a quota issue
            if "quota" in response.text.lower() or "429" in str(response.status_code):
                print("\n⚠️ You've hit your ElevenLabs quota limit!")
                print("Free tier: 10,000 characters per month")
                print("Check usage at: https://elevenlabs.io/app/usage")
            return
            
    except Exception as e:
        print(f"❌ Error connecting to ElevenLabs: {e}")
        return
    
    # Now test speech-to-text (if we have a sample audio file)
    print("\n2. Testing speech-to-text (requires audio file)...")
    
    # Create a simple test tone (we'll need a real audio file for this)
    # For now, just check if the endpoint exists
    stt_headers = {
        "xi-api-key": api_key,
        "Content-Type": "application/json"
    }
    
    # This is just to check if the endpoint exists - won't actually transcribe
    try:
        response = requests.options(
            "https://api.elevenlabs.io/v1/speech-to-text",
            headers=stt_headers
        )
        print(f"Speech-to-text endpoint status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Speech-to-text endpoint is accessible")
        else:
            print(f"⚠️ Speech-to-text endpoint returned {response.status_code}")
            print("Your ElevenLabs plan might not include speech-to-text")
            print("Check your plan at: https://elevenlabs.io/app/subscription")
            
    except Exception as e:
        print(f"❌ Could not reach speech-to-text endpoint: {e}")

if __name__ == "__main__":
    test_elevenlabs_speech_to_text()
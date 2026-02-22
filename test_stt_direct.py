import os
import requests
import base64
from dotenv import load_dotenv

load_dotenv()

def test_speech_to_text():
    api_key = os.getenv("ELEVENLABS_API_KEY")
    
    # Create a simple test audio file (you'll need a real audio file)
    # For testing, you can record a short WAV file
    audio_file = "test_audio.wav"  # Create a 2-second WAV file
    
    if not os.path.exists(audio_file):
        print(f"❌ Please create {audio_file} first")
        return
    
    with open(audio_file, "rb") as f:
        audio_base64 = base64.b64encode(f.read()).decode('utf-8')
    
    headers = {
        "xi-api-key": api_key,
        "Content-Type": "application/json"
    }
    
    data = {
        "audio": audio_base64,
        "model_id": "scribe_v1"
    }
    
    print("Testing ElevenLabs Speech-to-Text...")
    response = requests.post(
        "https://api.elevenlabs.io/v1/speech-to-text",
        headers=headers,
        json=data
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")

if __name__ == "__main__":
    test_speech_to_text()
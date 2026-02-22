# example.py
import os
from dotenv import load_dotenv
from io import BytesIO
from flask import Flask, request, jsonify
from elevenlabs.client import ElevenLabs

load_dotenv()

app = Flask(__name__)

#Elevenlabs set up
eleven = ElevenLabs(api_key=os.getenv("sk_cddc283309b650b70a555f5e0438ee58d01be2c2f1d0de96"))

#Supabase setup
'''audio_url = (
    "https://storage.googleapis.com/eleven-public-cdn/audio/marketing/nicole.mp3"
)
response = request.get(audio_url)
audio_data = BytesIO(response.content)'''
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv()
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.route("/transcribe", methods=["POST"])

def transcribe():
    audio_file = request.files["audio"]
    response = eleven.speech_to_text.convert(file = audio_file)

    transcript = response.text

    #Inserting transcript into Supabase

    supabase.table("text_entries".insert)
transcription = elevenlabs.speech_to_text.convert(
    file=audio_data,
    model_id="scribe_v2", # Model to use
    tag_audio_events=True, # Tag audio events like laughter, applause, etc.
    language_code="eng", # Language of the audio file. If set to None, the model will detect the language automatically.
    diarize=True, # Whether to annotate who is speaking
)

print(transcription.text)

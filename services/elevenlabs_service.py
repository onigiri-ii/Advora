from flask import Flask, request, jsonify
from elevenlabs.client import ElevenLabs
from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

<<<<<<< HEAD
#Elevenlabs set up
eleven = ElevenLabs(api_key=os.getenv("sk_cddc283309b650b70a555f5e0438ee58d01be2c2f1d0de96"))
=======
# ElevenLabs setup
eleven = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))
>>>>>>> e5870d76da0159c006488a79e93bb7584f4bbb8c

# Supabase setup
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.route("/transcribe", methods=["POST"])
def transcribe():
    audio_file = request.files["audio"]

    # Send audio to ElevenLabs
    response = eleven.speech_to_text.convert(
        file=audio_file
    )

    transcript = response.text

    # Insert transcript into Supabase
    supabase.table("symptom_entries").insert({
        "text": transcript
    }).execute()

    return jsonify({"transcript": transcript})

if __name__ == "__main__":
    app.run(debug=True)
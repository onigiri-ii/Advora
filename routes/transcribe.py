from flask import Blueprint, request, jsonify, session
from services.elevenlabs_service import ElevenLabsService

# Create blueprint FIRST
transcribe_bp = Blueprint('transcribe', __name__)

# Initialize ElevenLabs service
try:
    elevenlabs = ElevenLabsService()
    print("✅ ElevenLabs route handler initialized")
except Exception as e:
    print(f"⚠️  Warning: ElevenLabs service not initialized: {e}")
    elevenlabs = None

@transcribe_bp.route('/api/transcribe', methods=['POST'])
def transcribe_audio():
    """Transcribe audio using ElevenLabs API"""
    
    # Check if user is authenticated
    user_id = session.get('user_id')
    if not user_id:
        print("❌ Transcription attempted without authentication")
        return jsonify({'error': 'Not authenticated'}), 401
    
    # Check if ElevenLabs is available
    if not elevenlabs:
        print("❌ ElevenLabs service not available")
        return jsonify({'error': 'Transcription service not available'}), 500
    
    # Get audio data from request
    data = request.json
    if not data:
        print("❌ No JSON data in request")
        return jsonify({'error': 'No data provided'}), 400
        
    audio_base64 = data.get('audio')
    
    if not audio_base64:
        print("❌ No audio data in request")
        return jsonify({'error': 'No audio data provided'}), 400
    
    try:
        print(f"📝 Processing transcription request for user {user_id}")
        
        # Transcribe the audio
        transcript = elevenlabs.transcribe_audio(audio_base64)
        
        if transcript:
            print(f"✅ Transcription successful: {transcript[:100]}")
            return jsonify({'transcript': transcript}), 200
        else:
            print("❌ Transcription failed - no transcript returned")
            return jsonify({'error': 'Transcription failed'}), 500
            
    except Exception as e:
        print(f"❌ Error in transcribe endpoint: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@transcribe_bp.route('/api/transcribe/test', methods=['GET'])
def test_transcribe():
    """Test endpoint to check if ElevenLabs is configured"""
    if elevenlabs:
        return jsonify({
            'status': 'ok',
            'message': 'ElevenLabs service is initialized',
            'api_key_prefix': elevenlabs.api_key[:8] + '...' if elevenlabs.api_key else 'None'
        }), 200
    else:
        return jsonify({
            'status': 'error',
            'message': 'ElevenLabs service is not available'
        }), 500
# First, import dependencies
from flask import Blueprint, request, jsonify, session
from services.supabase_client import SupabaseService
from services.elevenlabs_service import ElevenLabsService
from services.gemini_service import GeminiService
from datetime import datetime
import json

# 1. CREATE THE BLUEPRINT FIRST (this must come before any @entries_bp decorators)
entries_bp = Blueprint('entries', __name__)

# 2. Initialize services
supabase = SupabaseService()
elevenlabs = ElevenLabsService()
gemini = GeminiService()

# 3. NOW define routes using the blueprint
@entries_bp.route('/api/transcribe', methods=['POST'])
def transcribe_audio():
    """Transcribe audio from voice memo"""
    print(f"Session data: {dict(session)}")
    user_id = session.get('user_id')
    print(f"User ID from session: {user_id}")
    
    # For testing, let's bypass auth temporarily
    # if not user_id:
    #     return jsonify({'error': 'Not authenticated'}), 401
    
    data = request.json
    audio_base64 = data.get('audio')
    
    if not audio_base64:
        return jsonify({'error': 'No audio data'}), 400
    
    # Call ElevenLabs API
    transcript = elevenlabs.transcribe_audio(audio_base64)
    
    if transcript:
        return jsonify({'transcript': transcript})
    else:
        return jsonify({'error': 'Transcription failed'}), 500

@entries_bp.route('/api/entries', methods=['GET'])
def get_entries():
    """Get entries for authenticated user"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Not authenticated'}), 401
    
    days = request.args.get('days', 30, type=int)
    entries = supabase.get_entries(user_id, days)
    return jsonify(entries)

@entries_bp.route('/api/entries/today', methods=['GET'])
def get_today_entry():
    """Get today's entry"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Not authenticated'}), 401
    
    today = datetime.now().strftime('%Y-%m-%d')
    entry = supabase.get_entry_by_date(user_id, today)
    return jsonify(entry or {})

@entries_bp.route('/api/entries', methods=['POST'])
def create_entry():
    """Create or update entry"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Not authenticated'}), 401
    
    data = request.json
    entry_data = {
        'entry_date': data.get('entry_date'),
        'symptoms': data.get('symptoms', []),
        'pain_level': data.get('pain_level'),
        'text_input': data.get('text_input', ''),
        'audio_transcript': data.get('audio_transcript', ''),
        'factors': data.get('factors', {})
    }
    
    # Check if entry exists for today
    existing = supabase.get_entry_by_date(user_id, entry_data['entry_date'])
    
    if existing:
        result = supabase.update_entry(existing['id'], entry_data)
    else:
        result = supabase.create_entry(user_id, entry_data)
    
    return jsonify({'success': True, 'data': result})

@entries_bp.route('/api/insights', methods=['GET'])
def get_insights():
    """Get AI-powered insights"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Not authenticated'}), 401
    
    # Get last 30 days of entries
    entries = supabase.get_entries(user_id, 30)
    
    if not entries:
        return jsonify({'message': 'Not enough data'})
    
    # Analyze with Gemini
    analysis = gemini.analyze_patterns(entries)
    
    # Calculate statistics
    pain_levels = [e['pain_level'] for e in entries if e.get('pain_level')]
    period_entries = [e for e in entries if e.get('factors') and e['factors'].get('period')]
    
    insights = {
        'analysis': analysis,
        'stats': {
            'total_entries': len(entries),
            'avg_pain': sum(pain_levels) / len(pain_levels) if pain_levels else 0,
            'avg_period_pain': sum([e['pain_level'] for e in period_entries if e.get('pain_level')]) / len(period_entries) if period_entries else 0,
            'most_common_symptoms': calculate_common_symptoms(entries)
        }
    }
    
    return jsonify(insights)

def calculate_common_symptoms(entries):
    """Helper to calculate most common symptoms"""
    symptom_counts = {}
    for entry in entries:
        for symptom in entry.get('symptoms', []):
            symptom_counts[symptom] = symptom_counts.get(symptom, 0) + 1
    
    sorted_symptoms = sorted(symptom_counts.items(), key=lambda x: x[1], reverse=True)
    return sorted_symptoms[:5]
from flask import Blueprint, request, jsonify, session
from services.supabase_client import SupabaseService
from services.elevenlabs_service import ElevenLabsService
from services.gemini_service import GeminiService
from datetime import datetime
import json

entries_bp = Blueprint('entries', __name__)
supabase = SupabaseService()
elevenlabs = ElevenLabsService()
gemini = GeminiService()

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
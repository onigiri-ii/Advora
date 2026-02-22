# from flask import Flask, render_template

# app = Flask(__name__)

# @app.route("/")
# def home():
#     return render_template("index.html")

# if __name__ == "__main__":
#     app.run(debug=True)
from flask import Flask, render_template, request, jsonify, session
from supabase_client import supabase
from gemini_service import GeminiService
from elevenlabs_service import ElevenLabsService
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "hackathon-secret-key")

# Initialize services
gemini = GeminiService()
elevenlabs = ElevenLabsService()

# For MVP, we'll use a default username
# In a real app, this would come from login
DEFAULT_USERNAME = "sarah"

# ========== YOUR EXISTING ROUTE - KEPT EXACTLY AS IS ==========
@app.route("/")
def home():
    return render_template("index.html")

# ========== NEW API ROUTES TO ADD BELOW ==========

@app.route('/api/entries', methods=['GET'])
def get_entries():
    """Get all entries for the current user"""
    username = request.args.get('username', DEFAULT_USERNAME)
    entries = supabase.get_user_entries(username)
    return jsonify(entries.data)

@app.route('/api/entries/today', methods=['GET'])
def get_today_entry():
    """Get today's entry"""
    username = request.args.get('username', DEFAULT_USERNAME)
    today = datetime.now().date().isoformat()
    entry = supabase.get_entry_by_date(username, today)
    return jsonify(entry.data[0] if entry.data else None)

@app.route('/api/entries', methods=['POST'])
def create_entry():
    """Create a new entry"""
    data = request.json
    username = data.get('username', DEFAULT_USERNAME)
    
    # Prepare entry data for Supabase
    entry_data = {
        'username': username,
        'entry_date': data.get('entry_date', datetime.now().date().isoformat()),
        'raw_text': data.get('text', ''),
        'pain_level': data.get('painLevel'),
        'stress_level': data.get('stressLevel'),
        'symptoms': data.get('symptoms', []),
        'mood': data.get('mood'),
        'title': data.get('title', '')
    }
    
    # Handle health factors
    factors = data.get('factors', {})
    if factors.get('period'):
        entry_data['period_flow'] = factors.get('periodFlow')
    if factors.get('birthControl'):
        entry_data['birth_control_type'] = factors.get('birthControlType')
    if factors.get('sick'):
        entry_data['sick_type'] = factors.get('sickType')
    
    # Save to Supabase
    result = supabase.create_entry(entry_data)
    
    # Generate AI insights (optional)
    if result.data and data.get('text'):
        try:
            insight = gemini.analyze_entry(data.get('text'))
            # You could save insights to a separate table here
            print(f"AI Insight: {insight}")
        except Exception as e:
            print(f"Gemini error: {e}")
    
    return jsonify({
        'success': True,
        'entry': result.data[0] if result.data else None
    })

@app.route('/api/insights', methods=['GET'])
def get_insights():
    """Get insights/analytics for a user"""
    username = request.args.get('username', DEFAULT_USERNAME)
    
    # Get entries
    entries = supabase.get_user_entries(username)
    
    if not entries.data:
        return jsonify({'error': 'No entries found'})
    
    # Calculate insights
    pain_levels = [e['pain_level'] for e in entries.data if e.get('pain_level')]
    avg_pain = sum(pain_levels) / len(pain_levels) if pain_levels else 0
    
    # Symptom frequency
    symptom_count = {}
    for entry in entries.data:
        for symptom in entry.get('symptoms', []):
            symptom_count[symptom] = symptom_count.get(symptom, 0) + 1
    
    # Period pain correlation
    period_entries = [e for e in entries.data if e.get('period_flow')]
    period_pain = [e['pain_level'] for e in period_entries if e.get('pain_level')]
    avg_period_pain = sum(period_pain) / len(period_pain) if period_pain else 0
    
    return jsonify({
        'total_entries': len(entries.data),
        'avg_pain': round(avg_pain, 1),
        'avg_period_pain': round(avg_period_pain, 1),
        'top_symptoms': sorted(symptom_count.items(), key=lambda x: x[1], reverse=True)[:5],
        'pain_trend': [
            {'date': e['entry_date'], 'pain': e['pain_level']} 
            for e in entries.data[:14]  # Last 14 days
        ]
    })

@app.route('/api/voice/process', methods=['POST'])
def process_voice():
    """Process voice input (mock for now)"""
    data = request.json
    # In real app, you'd use ElevenLabs here
    return jsonify({
        'transcript': "I have a headache and feel tired",
        'success': True
    })

# Test endpoint to check if Supabase is connected
@app.route('/api/test', methods=['GET'])
def test_connection():
    """Test Supabase connection"""
    try:
        result = supabase.client.table('entries').select('*').limit(1).execute()
        return jsonify({
            'status': 'connected',
            'message': ' Supabase connection successful!',
            'data': result.data
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f' Supabase connection failed: {str(e)}'
        })

if __name__ == "__main__":
    # Test Supabase connection on startup
    print(" Testing Supabase connection...")
    try:
        test_result = supabase.client.table('entries').select('*').limit(1).execute()
        print(" Supabase connected successfully!")
    except Exception as e:
        print(f"  Warning: Supabase connection issue: {e}")
        print("   The app will still run, but database features won't work.")
    
    print("Starting Flask server on http://127.0.0.1:5000")
    app.run(debug=True)
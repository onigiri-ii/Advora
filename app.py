from flask import Flask, render_template, session, jsonify
from dotenv import load_dotenv
import os
from datetime import timedelta

# Load environment variables first
load_dotenv()

# Import blueprints after loading env
from routes.auth import auth_bp
from routes.entries import entries_bp
from routes.transcribe import transcribe_bp
from services.supabase_service import supabase_service

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev-secret-key")
app.permanent_session_lifetime = timedelta(days=7)
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True if using HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(entries_bp)
app.register_blueprint(transcribe_bp)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/api/health")
def health_check():
    """Check if Supabase is connected"""
    if supabase_service:
        try:
            supabase = supabase_service.get_client()
            supabase.table('symptoms').select('count', count='exact').limit(1).execute()
            return jsonify({"status": "healthy", "supabase": "connected"}), 200
        except Exception as e:
            return jsonify({"status": "unhealthy", "error": str(e)}), 500
    else:
        return jsonify({"status": "unhealthy", "error": "Supabase service not initialized"}), 500

@app.route("/api/debug/app-session")
def debug_app_session():
    """Debug endpoint to check session from app root"""
    return jsonify({
        'session': dict(session),
        'cookies': request.cookies.get('session')
    }), 200

if __name__ == "__main__":
    app.run(debug=True)
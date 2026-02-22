from flask import Blueprint, jsonify
from services.supabase_client import supabase
from services.gemini_service import generate_insights

insights_bp = Blueprint("insights", __name__)

@insights_bp.route("/generate-insights", methods=["GET"])
def generate():
    entries = supabase.table("entries").select("*").execute()

    ai_response = generate_insights(entries.data)

    return jsonify({"insight": ai_response})
# routes/entries.py

from flask import Blueprint, request, jsonify
from services.supabase_client import supabase

entries_bp = Blueprint("entries", __name__)

@entries_bp.route("/save-entry", methods=["POST"])
def save_entry():
    data = request.json

    response = supabase.table("entries").insert(data).execute()

    return jsonify(response.data)
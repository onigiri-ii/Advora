import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

class SupabaseService:
    def __init__(self):
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        if not url or not key:
            raise ValueError("Missing Supabase credentials in .env file")
        self.supabase: Client = create_client(url, key)
    
    def create_entry(self, user_id, entry_data):
        data = {
            "user_id": user_id,
            "entry_date": entry_data["entry_date"],
            "symptoms": entry_data["symptoms"],
            "pain_level": entry_data["pain_level"],
            "text_input": entry_data.get("text_input", ""),
            "audio_transcript": entry_data.get("audio_transcript", ""),
            "factors": entry_data.get("factors", {})
        }
        result = self.supabase.table("symptom_entries").insert(data).execute()
        return result.data
    
    def get_entries(self, user_id, days=30):
        result = self.supabase.table("symptom_entries")\
            .select("*")\
            .eq("user_id", user_id)\
            .order("entry_date", desc=True)\
            .limit(days)\
            .execute()
        return result.data
    
    def get_entry_by_date(self, user_id, date):
        result = self.supabase.table("symptom_entries")\
            .select("*")\
            .eq("user_id", user_id)\
            .eq("entry_date", date)\
            .execute()
        return result.data[0] if result.data else None
    
    def update_entry(self, entry_id, entry_data):
        result = self.supabase.table("symptom_entries")\
            .update(entry_data)\
            .eq("id", entry_id)\
            .execute()
        return result.data
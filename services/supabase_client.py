import os
from supabase import create_client, Client
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

class SupabaseClient:
    def __init__(self):
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        
        if not url or not key:
            raise ValueError("Missing Supabase credentials in .env file")
        
        self.client: Client = create_client(url, key)
    
    # ========== ENTRIES METHODS ==========
    def create_entry(self, entry_data):
        """
        Create a new journal entry
        Expected entry_data format:
        {
            'username': 'sarah',
            'entry_date': '2026-02-21',
            'raw_text': 'I have a headache...',
            'pain_level': 7,
            'stress_level': 3,
            'symptoms': ['headache', 'fatigue'],
            'period_flow': 'medium',  # or None
            'birth_control_type': 'pill',  # or None
            'sick_type': 'cold',  # or None
            'mood': 'tired',
            'title': 'Today's entry'
        }
        """
        # Add timestamps
        entry_data['created_at'] = datetime.now().isoformat()
        
        # Convert symptoms list to JSON if it's a list
        if 'symptoms' in entry_data and isinstance(entry_data['symptoms'], list):
            entry_data['symptoms'] = entry_data['symptoms']
        
        # Handle empty factors (convert None/False to null)
        for field in ['period_flow', 'birth_control_type', 'sick_type']:
            if field not in entry_data or not entry_data[field]:
                entry_data[field] = None
        
        return self.client.table('entries').insert(entry_data).execute()
    
    def get_user_entries(self, username, limit=50):
        """Get all entries for a user"""
        return self.client.table('entries')\
            .select('*')\
            .eq('username', username)\
            .order('entry_date', desc=True)\
            .limit(limit)\
            .execute()
    
    def get_entry_by_date(self, username, entry_date):
        """Get entry for a specific date"""
        return self.client.table('entries')\
            .select('*')\
            .eq('username', username)\
            .eq('entry_date', entry_date)\
            .execute()
    
    def update_entry(self, entry_id, updates):
        """Update an entry"""
        updates['updated_at'] = datetime.now().isoformat()
        return self.client.table('entries')\
            .update(updates)\
            .eq('id', entry_id)\
            .execute()
    
    def delete_entry(self, entry_id):
        """Delete an entry"""
        return self.client.table('entries')\
            .delete()\
            .eq('id', entry_id)\
            .execute()
    
    # ========== USER PROFILE METHODS (optional) ==========
    def create_user_profile(self, username, display_name=None, age=None):
        """Create a user profile"""
        data = {
            'username': username,
            'display_name': display_name or username,
            'age': age,
            'last_active': datetime.now().date().isoformat()
        }
        return self.client.table('user_profiles').insert(data).execute()
    
    def get_user_profile(self, username):
        """Get user profile"""
        return self.client.table('user_profiles')\
            .select('*')\
            .eq('username', username)\
            .execute()
    
    # ========== ANALYTICS METHODS ==========
    def get_symptom_frequency(self, username, days=30):
        """Get frequency of symptoms for a user"""
        # This uses a SQL function, but for simplicity, we'll get entries and count in Python
        entries = self.get_user_entries(username, limit=100)
        
        symptom_count = {}
        if entries.data:
            for entry in entries.data:
                symptoms = entry.get('symptoms', [])
                if isinstance(symptoms, list):
                    for symptom in symptoms:
                        symptom_count[symptom] = symptom_count.get(symptom, 0) + 1
        
        return symptom_count
    
    def get_pain_trend(self, username, days=14):
        """Get pain levels for the last N days"""
        entries = self.get_user_entries(username, limit=days)
        
        trend_data = []
        if entries.data:
            for entry in entries.data:
                trend_data.append({
                    'date': entry['entry_date'],
                    'pain_level': entry['pain_level']
                })
        
        return sorted(trend_data, key=lambda x: x['date'])

# Create a single instance to reuse
supabase = SupabaseClient()

# Test function
def test_connection():
    try:
        # Try to query the entries table
        result = supabase.client.table('entries').select('*').limit(1).execute()
        print("Connection successful!")
        print(f"Found {len(result.data)} entries")
        return True
    except Exception as e:
        print(f"Connection failed: {e}")
        return False

if __name__ == "__main__":
    test_connection()
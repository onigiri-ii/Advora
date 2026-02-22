import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

class SupabaseService:
    def __init__(self):
        self.url = os.getenv("SUPABASE_URL")
        self.key = os.getenv("SUPABASE_KEY")
        
        if not self.url or not self.key:
            raise ValueError("Missing Supabase credentials")
        
        self.client: Client = create_client(self.url, self.key)
        print(f"✅ Supabase connected to: {self.url}")
    
    def get_client(self):
        return self.client

# Create a singleton instance
supabase_service = SupabaseService()
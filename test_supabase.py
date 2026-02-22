import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

# Get credentials
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

print(f"URL: {url}")
print(f"Key starts with: {key[:10]}...")

# Connect to Supabase
supabase = create_client(url, key)

# Try to query users
try:
    result = supabase.table('users').select('*').execute()
    print(f"\n✅ Connection successful!")
    print(f"Found {len(result.data)} users:")
    for user in result.data:
        print(f"  - {user['email']} | Password: {user['password']}")
except Exception as e:
    print(f"\n❌ Error: {e}")
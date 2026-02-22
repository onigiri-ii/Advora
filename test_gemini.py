from google import genai
import os
from dotenv import load_dotenv

load_dotenv()

def test_gemini():
    api_key = os.getenv("GEMINI_API_KEY")
    print(f"API Key exists: {'Yes' if api_key else 'No'}")
    if api_key:
        print(f"API Key starts with: {api_key[:8]}...")
    
    try:
        # Initialize client
        client = genai.Client(api_key=api_key)
        print("✅ Client initialized")
        
        # Test 1: List models (new SDK uses different method)
        print("\n1. Testing with gemini-2.5-flash-lite...")
        response = client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents="Say hello in one word"
        )
        print(f"✅ Success! Response: {response.text}")
        
        
    except Exception as e:
        print(f"\n❌ Error: {type(e).__name__}")
        print(f"Message: {str(e)}")

if __name__ == "__main__":
    test_gemini()
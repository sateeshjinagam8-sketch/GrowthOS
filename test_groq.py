from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv('.env')

api_key = os.getenv('GROQ_API_KEY')

if not api_key:
    print("❌ API key not found in .env file!")
else:
    print(f"✅ API key loaded: {api_key[:10]}...")
    try:
        client = Groq(api_key=api_key)
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": "Say hello in one line"}]
        )
        print("✅ Groq is working!")
        print("AI says:", response.choices[0].message.content)
    except Exception as e:
        print(f"❌ Groq error: {e}")
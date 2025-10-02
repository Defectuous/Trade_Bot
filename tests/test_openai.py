#!/usr/bin/env python3
"""
Quick test script for OpenAI API key validation
"""
import os
from dotenv import load_dotenv
import openai

def test_openai_api():
    print("🧪 Testing OpenAI API Configuration...")
    
    # Load environment variables
    load_dotenv()
    api_key = os.getenv('OPENAI_API_KEY')
    
    if not api_key:
        print("❌ OPENAI_API_KEY not found in .env file")
        return False
    
    print(f"🔑 API Key found: {api_key[:15]}...")
    
    try:
        # Test API connection
        client = openai.OpenAI(api_key=api_key)
        
        # Simple test request
        response = client.chat.completions.create(
            model='gpt-3.5-turbo',
            messages=[
                {'role': 'system', 'content': 'You are a helpful trading assistant.'},
                {'role': 'user', 'content': 'What does RSI mean in trading? Answer in one sentence.'}
            ],
            max_tokens=50,
            temperature=0.7
        )
        
        print("✅ OpenAI API test successful!")
        print(f"📝 Response: {response.choices[0].message.content}")
        print(f"💰 Tokens used: {response.usage.total_tokens}")
        return True
        
    except openai.AuthenticationError:
        print("❌ Invalid API key. Please check your OpenAI API key.")
        print("🔗 Get a new key at: https://platform.openai.com/account/api-keys")
        return False
        
    except openai.RateLimitError:
        print("⚠️  Rate limit exceeded. Wait a moment and try again.")
        return False
        
    except Exception as e:
        print(f"❌ Error testing OpenAI API: {e}")
        return False

if __name__ == "__main__":
    success = test_openai_api()
    if success:
        print("\n🎉 OpenAI integration is ready for trading bot!")
    else:
        print("\n🔧 Please fix the API key before running the trading bot.")
import asyncio
import aiohttp
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_correct_minimax_api():
    """Test the correct MiniMax API endpoints"""
    
    api_key = os.getenv("MINIMAX_API_KEY")
    group_id = os.getenv("MINIMAX_GROUP_ID") 
    
    if not api_key or not group_id:
        print("❌ Missing API credentials")
        return
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Test different possible endpoints with correct base URL
    endpoints_to_test = [
        f"https://api.minimax.io/v1/files?GroupId={group_id}",
        f"https://api.minimax.io/v1/audio/files?GroupId={group_id}",
        f"https://api.minimax.io/v1/audio/voice-cloning?GroupId={group_id}",
        f"https://api.minimax.io/v1/t2a_pro?GroupId={group_id}",
        f"https://api.minimax.io/v1/speech?GroupId={group_id}",
    ]
    
    print("🔍 Testing correct MiniMax API (minimax.io)...")
    
    async with aiohttp.ClientSession() as session:
        for endpoint in endpoints_to_test:
            try:
                print(f"\n📡 Testing: {endpoint}")
                async with session.get(endpoint, headers=headers, timeout=10) as response:
                    print(f"   Status: {response.status}")
                    if response.status != 404:
                        text = await response.text()
                        print(f"   Response preview: {text[:200]}...")
                        if response.status == 200:
                            print("   ✅ WORKING ENDPOINT FOUND!")
                    else:
                        print("   ❌ 404 Not Found")
            except Exception as e:
                print(f"   ❌ Error: {str(e)}")
    
    # Test TTS with correct URL
    print("\n🎤 Testing TTS with correct API...")
    async with aiohttp.ClientSession() as session:
        payload = {
            "model": "speech-01",
            "voice_id": "male-qn-qingse",
            "text": "Hello, this is a test.",
            "stream": False
        }
        
        try:
            async with session.post(
                f"https://api.minimax.io/v1/t2a_pro?GroupId={group_id}",
                headers=headers,
                json=payload,
                timeout=30
            ) as response:
                print(f"TTS Status: {response.status}")
                result = await response.text()
                print(f"TTS Response: {result[:300]}...")
        except Exception as e:
            print(f"TTS Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_correct_minimax_api())
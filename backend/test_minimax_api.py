import asyncio
import aiohttp
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_minimax_api():
    """Test the actual Minimax API to see response structure"""
    
    api_key = os.getenv("MINIMAX_API_KEY")
    group_id = os.getenv("MINIMAX_GROUP_ID") 
    
    if not api_key or not group_id:
        print("❌ Missing API credentials")
        return
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Test 1: List files endpoint (should work)
    print("🔍 Testing files list endpoint...")
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(
                f"https://api.minimaxi.chat/v1/files?GroupId={group_id}",
                headers=headers,
                timeout=30
            ) as response:
                print(f"Files endpoint status: {response.status}")
                if response.status == 200:
                    result = await response.json()
                    print("✅ Files endpoint working")
                    print(f"Response structure: {list(result.keys()) if isinstance(result, dict) else type(result)}")
                else:
                    text = await response.text()
                    print(f"❌ Files endpoint failed: {text}")
        except Exception as e:
            print(f"❌ Files endpoint error: {str(e)}")
    
    # Test 2: Test speech generation with a simple request
    print("\n🔍 Testing speech generation endpoint...")
    async with aiohttp.ClientSession() as session:
        try:
            payload = {
                "model": "speech-01",
                "voice_id": "male-qn-qingse",  # Using a default voice ID
                "text": "Hello, this is a test of the Minimax API.",
                "stream": False
            }
            
            async with session.post(
                f"https://api.minimaxi.chat/v1/t2a_pro?GroupId={group_id}",
                headers=headers,
                json=payload,
                timeout=60
            ) as response:
                print(f"Speech generation status: {response.status}")
                if response.status == 200:
                    result = await response.json()
                    print("✅ Speech generation working")
                    print(f"Response keys: {list(result.keys()) if isinstance(result, dict) else type(result)}")
                    
                    # Print the full response structure (truncated)
                    print("Response structure:")
                    for key, value in result.items():
                        if isinstance(value, str) and len(value) > 100:
                            print(f"  {key}: '{value[:100]}...' (truncated)")
                        else:
                            print(f"  {key}: {value}")
                else:
                    text = await response.text()
                    print(f"❌ Speech generation failed: {response.status} - {text}")
        except Exception as e:
            print(f"❌ Speech generation error: {str(e)}")
    
    # Test 3: Test voice clone endpoint
    print("\n🔍 Testing voice clone endpoint structure...")
    async with aiohttp.ClientSession() as session:
        try:
            payload = {
                "file_id": "test_file_id",  # This will fail but show us the expected structure
                "voice_id": "test_voice",
                "model": "speech-01"
            }
            
            async with session.post(
                f"https://api.minimaxi.chat/v1/voice_clone?GroupId={group_id}",
                headers=headers,
                json=payload,
                timeout=60
            ) as response:
                print(f"Voice clone status: {response.status}")
                text = await response.text()
                print(f"Voice clone response: {text}")
        except Exception as e:
            print(f"❌ Voice clone error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_minimax_api())
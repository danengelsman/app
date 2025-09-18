import asyncio
import aiohttp
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_different_endpoints():
    """Test different possible Minimax API endpoints"""
    
    api_key = os.getenv("MINIMAX_API_KEY")
    group_id = os.getenv("MINIMAX_GROUP_ID")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Different possible base URLs and endpoints to test
    endpoints_to_test = [
        # Original format
        f"https://api.minimaxi.chat/v1/files?GroupId={group_id}",
        
        # Alternative formats
        f"https://api.minimaxi.chat/v1/audio/upload?GroupId={group_id}",
        f"https://api.minimaxi.chat/v1/voice/upload?GroupId={group_id}",
        f"https://api.minimaxi.chat/v2/files?GroupId={group_id}",
        f"https://api.minimaxi.chat/v2/voice/upload?GroupId={group_id}",
        
        # Speech-02 series endpoints
        f"https://api.minimaxi.chat/v1/speech/upload?GroupId={group_id}",
        f"https://api.minimaxi.chat/v1/speech-02/upload?GroupId={group_id}",
        
        # Different base domain
        f"https://api.minimax.io/v1/files?GroupId={group_id}",
        f"https://api.minimax.io/v1/audio/upload?GroupId={group_id}",
    ]
    
    async with aiohttp.ClientSession() as session:
        for endpoint in endpoints_to_test:
            try:
                print(f"\n🔍 Testing: {endpoint}")
                async with session.get(endpoint, headers=headers, timeout=10) as response:
                    print(f"   Status: {response.status}")
                    if response.status != 404:
                        text = await response.text()
                        print(f"   Response: {text[:200]}...")
                        if response.status == 200:
                            print("   ✅ WORKING ENDPOINT FOUND!")
                    else:
                        print("   ❌ 404 Not Found")
            except Exception as e:
                print(f"   ❌ Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_different_endpoints())
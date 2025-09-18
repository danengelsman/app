import asyncio
import aiohttp
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_working_endpoints():
    """Test endpoints that we know work"""
    
    api_key = os.getenv("MINIMAX_API_KEY")
    group_id = os.getenv("MINIMAX_GROUP_ID")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Test the working TTS endpoint to see its full structure
    print("🔍 Testing working TTS endpoint structure...")
    
    async with aiohttp.ClientSession() as session:
        payload = {
            "model": "speech-01",
            "voice_id": "male-qn-qingse",  # Default voice
            "text": "Hello test",
            "stream": False
        }
        
        async with session.post(
            f"https://api.minimaxi.chat/v1/t2a_pro?GroupId={group_id}",
            headers=headers,
            json=payload,
            timeout=30
        ) as response:
            print(f"Status: {response.status}")
            result = await response.json()
            print("Response structure:")
            for key, value in result.items():
                if isinstance(value, dict):
                    print(f"  {key}: {value}")
                else:
                    print(f"  {key}: {type(value).__name__}")
    
    # Test if voice cloning works with the same endpoint but different parameters
    print("\n🔍 Testing voice clone with t2a_pro endpoint...")
    
    async with aiohttp.ClientSession() as session:
        payload = {
            "model": "speech-01",
            "voice_id": "custom_voice_test",  # Custom voice ID
            "text": "This is a test of custom voice",
            "stream": False
        }
        
        async with session.post(
            f"https://api.minimaxi.chat/v1/t2a_pro?GroupId={group_id}",
            headers=headers,
            json=payload,
            timeout=30
        ) as response:
            print(f"Status: {response.status}")
            result = await response.json()
            print("Custom voice response:")
            for key, value in result.items():
                if isinstance(value, dict):
                    print(f"  {key}: {value}")
                else:
                    print(f"  {key}: {type(value).__name__}")

if __name__ == "__main__":
    asyncio.run(test_working_endpoints())
import asyncio
import aiohttp
import os
import base64
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_voice_clone_parameters():
    """Test different parameter combinations for voice cloning"""
    
    api_key = os.getenv("MINIMAX_API_KEY")
    group_id = os.getenv("MINIMAX_GROUP_ID")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Test different parameter combinations
    test_cases = [
        {
            "name": "With file_id",
            "payload": {
                "file_id": "test_file_id",
                "voice_id": "my_custom_voice",
                "model": "speech-01"
            }
        },
        {
            "name": "With audio_data base64",
            "payload": {
                "audio_data": base64.b64encode(b"fake audio content").decode(),
                "voice_id": "my_custom_voice", 
                "model": "speech-01"
            }
        },
        {
            "name": "With audio_url",
            "payload": {
                "audio_url": "https://example.com/audio.mp3",
                "voice_id": "my_custom_voice",
                "model": "speech-01"
            }
        },
        {
            "name": "With audio_file",
            "payload": {
                "audio_file": base64.b64encode(b"fake audio content").decode(),
                "voice_id": "my_custom_voice",
                "model": "speech-01"
            }
        },
        {
            "name": "With training_data",
            "payload": {
                "training_data": base64.b64encode(b"fake audio content").decode(),
                "voice_id": "my_custom_voice",
                "model": "speech-01"
            }
        },
        {
            "name": "Minimal params",
            "payload": {
                "voice_id": "my_custom_voice",
                "model": "speech-01"
            }
        }
    ]
    
    async with aiohttp.ClientSession() as session:
        for test_case in test_cases:
            try:
                print(f"\n🧪 Testing: {test_case['name']}")
                print(f"   Payload keys: {list(test_case['payload'].keys())}")
                
                async with session.post(
                    f"https://api.minimax.io/v1/voice_clone",
                    headers=headers,
                    json=test_case['payload'],
                    params={"GroupId": group_id},
                    timeout=15
                ) as response:
                    print(f"   Status: {response.status}")
                    result = await response.json()
                    
                    base_resp = result.get("base_resp", {})
                    status_code = base_resp.get("status_code", 0)
                    status_msg = base_resp.get("status_msg", "")
                    
                    print(f"   API Status Code: {status_code}")
                    print(f"   API Status Message: {status_msg}")
                    
                    if status_code == 0:
                        print("   ✅ SUCCESS! This parameter combination works!")
                    elif "invalid params" not in status_msg.lower():
                        print(f"   🔍 Different error - might be on the right track!")
                    
            except Exception as e:
                print(f"   ❌ Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_voice_clone_parameters())
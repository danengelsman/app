import asyncio
import aiohttp
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_file_upload_endpoints():
    """Test file upload endpoints with POST requests"""
    
    api_key = os.getenv("MINIMAX_API_KEY")
    group_id = os.getenv("MINIMAX_GROUP_ID") 
    
    headers = {
        "Authorization": f"Bearer {api_key}"
    }
    
    # Test file upload endpoints (these should be POST, not GET)
    upload_endpoints = [
        f"https://api.minimax.io/v1/files",
        f"https://api.minimax.io/v1/audio/files", 
        f"https://api.minimax.io/v1/upload",
        f"https://api.minimax.io/v1/audio/upload",
    ]
    
    print("📁 Testing file upload endpoints with POST...")
    
    # Create a small test file in memory
    test_file_content = b"fake audio content for testing"
    
    async with aiohttp.ClientSession() as session:
        for endpoint in upload_endpoints:
            try:
                print(f"\n📤 Testing POST: {endpoint}")
                
                # Create form data
                data = aiohttp.FormData()
                data.add_field('GroupId', group_id)
                data.add_field('purpose', 'voice_clone')
                data.add_field('file', test_file_content, filename='test.mp3', content_type='audio/mpeg')
                
                async with session.post(
                    endpoint,
                    headers=headers,
                    data=data,
                    timeout=15
                ) as response:
                    print(f"   Status: {response.status}")
                    text = await response.text()
                    print(f"   Response: {text[:300]}...")
                    
                    if response.status not in [404, 405]:  # Not "Not Found" or "Method Not Allowed"
                        print("   ✅ POTENTIAL WORKING ENDPOINT!")
                        
            except Exception as e:
                print(f"   ❌ Error: {str(e)}")
    
    # Test voice cloning endpoint
    print("\n🎵 Testing voice cloning endpoint...")
    async with aiohttp.ClientSession() as session:
        try:
            payload = {
                "file_id": "test_file_id",
                "voice_id": "test_voice", 
                "model": "speech-01"
            }
            
            async with session.post(
                f"https://api.minimax.io/v1/voice_clone",
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                json=payload,
                params={"GroupId": group_id},
                timeout=15
            ) as response:
                print(f"Voice clone status: {response.status}")
                text = await response.text()
                print(f"Voice clone response: {text[:300]}...")
                
        except Exception as e:
            print(f"Voice clone error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_file_upload_endpoints())
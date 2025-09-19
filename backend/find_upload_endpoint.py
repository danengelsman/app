import asyncio
import aiohttp
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def find_upload_endpoint():
    """Try to find the correct file upload endpoint"""
    
    api_key = os.getenv("MINIMAX_API_KEY")
    group_id = os.getenv("MINIMAX_GROUP_ID")
    
    # Try different possible upload endpoints
    potential_endpoints = [
        # Basic variations
        f"https://api.minimax.io/v1/file",
        f"https://api.minimax.io/v1/file/upload",
        f"https://api.minimax.io/v1/upload/file", 
        
        # Audio specific
        f"https://api.minimax.io/v1/audio/file",
        f"https://api.minimax.io/v1/audio/file/upload",
        f"https://api.minimax.io/v1/audio/upload/file",
        
        # Voice specific
        f"https://api.minimax.io/v1/voice/file", 
        f"https://api.minimax.io/v1/voice/upload",
        f"https://api.minimax.io/v1/voice/file/upload",
        
        # Speech specific
        f"https://api.minimax.io/v1/speech/file",
        f"https://api.minimax.io/v1/speech/upload",
        f"https://api.minimax.io/v1/speech/file/upload",
        
        # Other variations
        f"https://api.minimax.io/v1/media/upload",
        f"https://api.minimax.io/v1/resource/upload",
        f"https://api.minimax.io/upload",
        f"https://api.minimax.io/file/upload",
    ]
    
    headers = {
        "Authorization": f"Bearer {api_key}"
    }
    
    # Create minimal test file
    test_content = b"minimal test audio content"
    
    async with aiohttp.ClientSession() as session:
        for endpoint in potential_endpoints:
            try:
                print(f"\n📤 Testing: {endpoint}")
                
                # Try with form data
                data = aiohttp.FormData()
                data.add_field('file', test_content, filename='test.mp3', content_type='audio/mpeg')
                data.add_field('GroupId', group_id)
                data.add_field('purpose', 'voice_clone')
                
                async with session.post(
                    endpoint,
                    headers=headers,
                    data=data,
                    timeout=10
                ) as response:
                    print(f"   Status: {response.status}")
                    
                    if response.status == 200:
                        text = await response.text()
                        print(f"   ✅ SUCCESS! Response: {text[:200]}...")
                        return endpoint
                    elif response.status != 404:
                        text = await response.text()
                        print(f"   🔍 Non-404 response: {text[:200]}...")
                    else:
                        print("   ❌ 404 Not Found")
                        
            except Exception as e:
                print(f"   ❌ Error: {str(e)}")
    
    print("\n❌ No working file upload endpoint found")
    return None

if __name__ == "__main__":
    asyncio.run(find_upload_endpoint())
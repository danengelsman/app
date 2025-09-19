import asyncio
import aiohttp
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_direct_multipart_upload():
    """Test if voice clone endpoint accepts multipart files directly"""
    
    api_key = os.getenv("MINIMAX_API_KEY")
    group_id = os.getenv("MINIMAX_GROUP_ID")
    
    headers = {
        "Authorization": f"Bearer {api_key}"
    }
    
    # Create test audio content
    test_audio = b"fake mp3 audio content for testing"
    
    print("🎵 Testing direct multipart upload to voice_clone...")
    
    async with aiohttp.ClientSession() as session:
        # Try multipart form data directly to voice_clone endpoint
        data = aiohttp.FormData()
        data.add_field('file', test_audio, filename='test_voice.mp3', content_type='audio/mpeg')
        data.add_field('voice_id', 'test_voice_123')
        data.add_field('model', 'speech-01')
        data.add_field('GroupId', group_id)
        
        try:
            async with session.post(
                f"https://api.minimax.io/v1/voice_clone",
                headers=headers,
                data=data,
                timeout=20
            ) as response:
                print(f"Status: {response.status}")
                result = await response.text()
                print(f"Response: {result[:400]}...")
                
        except Exception as e:
            print(f"Error: {str(e)}")
    
    print("\n🔍 Testing if we can find API documentation endpoints...")
    
    # Sometimes APIs have documentation or help endpoints
    doc_endpoints = [
        "https://api.minimax.io/",
        "https://api.minimax.io/v1/",
        "https://api.minimax.io/docs",
        "https://api.minimax.io/v1/docs",
        "https://api.minimax.io/help",
        "https://api.minimax.io/v1/help",
        "https://api.minimax.io/api-docs",
        "https://api.minimax.io/.well-known/openapi",
    ]
    
    for endpoint in doc_endpoints:
        try:
            async with session.get(endpoint, timeout=5) as response:
                if response.status == 200:
                    text = await response.text()
                    print(f"✅ Found docs at {endpoint}: {text[:200]}...")
                elif response.status != 404:
                    print(f"🔍 {endpoint}: Status {response.status}")
        except:
            pass

if __name__ == "__main__":
    asyncio.run(test_direct_multipart_upload())
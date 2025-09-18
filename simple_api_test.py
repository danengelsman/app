import requests
import json

def test_api_endpoint(endpoint, description):
    url = f"https://emergent-content-1.preview.emergentagent.com/api/{endpoint}"
    print(f"\n🔍 Testing {description}")
    print(f"URL: {url}")
    
    try:
        response = requests.get(url, timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"✅ Success - Response keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                return True
            except:
                print(f"✅ Success - Response: {response.text[:100]}...")
                return True
        else:
            print(f"❌ Failed - {response.status_code}: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def main():
    print("🚀 Quick API Test")
    print("=" * 50)
    
    tests = [
        ("", "Basic Health Check"),
        ("agents/status", "Agents Status"),
        ("analytics/dashboard", "Analytics Dashboard"),
        ("trending-topics", "Trending Topics"),
        ("content", "Content Library"),
        ("branding", "Branding Kit"),
        ("blog-posts", "Blog Posts"),
        ("monetization/strategies", "Monetization Strategies")
    ]
    
    passed = 0
    total = len(tests)
    
    for endpoint, description in tests:
        if test_api_endpoint(endpoint, description):
            passed += 1
    
    print(f"\n📊 Results: {passed}/{total} tests passed")
    
    if passed < total:
        print("\n🔧 Checking backend logs for errors...")
        import subprocess
        try:
            result = subprocess.run(['tail', '-n', '20', '/var/log/supervisor/backend.err.log'], 
                                  capture_output=True, text=True)
            if result.stdout:
                print("Recent backend errors:")
                print(result.stdout)
        except:
            pass

if __name__ == "__main__":
    main()
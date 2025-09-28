import requests
import sys

def quick_test():
    base_url = "https://ai-creator-hub-53.preview.emergentagent.com"
    api_url = f"{base_url}/api"
    
    print("🔍 Quick Backend API Check")
    print("=" * 40)
    
    # Test basic endpoints
    endpoints = [
        ("Health Check", ""),
        ("Agents Status", "agents/status"),
        ("Trending Topics", "trending-topics"),
        ("Content Library", "content"),
        ("Analytics Dashboard", "analytics/dashboard")
    ]
    
    passed = 0
    total = len(endpoints)
    
    for name, endpoint in endpoints:
        url = f"{api_url}/{endpoint}" if endpoint else f"{api_url}/"
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                print(f"✅ {name}: OK ({response.status_code})")
                passed += 1
            else:
                print(f"❌ {name}: Failed ({response.status_code})")
        except Exception as e:
            print(f"❌ {name}: Error - {str(e)}")
    
    print(f"\n📊 Results: {passed}/{total} endpoints working")
    return passed == total

if __name__ == "__main__":
    success = quick_test()
    sys.exit(0 if success else 1)
import requests
import sys

def test_key_endpoints():
    """Test key endpoints needed for navigation testing"""
    base_url = "https://ai-creator-hub-53.preview.emergentagent.com/api"
    
    endpoints = [
        ("Health Check", "GET", ""),
        ("Trending Topics", "GET", "trending-topics"),
        ("Content Library", "GET", "content"),
        ("Analytics Dashboard", "GET", "analytics/dashboard"),
        ("Agents Status", "GET", "agents/status")
    ]
    
    results = []
    
    for name, method, endpoint in endpoints:
        url = f"{base_url}/{endpoint}" if endpoint else f"{base_url}/"
        
        try:
            print(f"Testing {name}...")
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ {name} - Status: {response.status_code}")
                
                # Check specific data for navigation testing
                if endpoint == "trending-topics":
                    topics = data.get('topics', [])
                    print(f"   Found {len(topics)} topics")
                    if len(topics) > 0:
                        print(f"   Sample topic: {topics[0].get('keyword', 'No keyword')}")
                
                elif endpoint == "content":
                    content = data.get('content', [])
                    print(f"   Found {len(content)} content items")
                    if len(content) > 0:
                        print(f"   Sample content: {content[0].get('title', 'No title')}")
                
                results.append((name, True, data))
            else:
                print(f"❌ {name} - Status: {response.status_code}")
                results.append((name, False, response.text))
                
        except Exception as e:
            print(f"❌ {name} - Error: {str(e)}")
            results.append((name, False, str(e)))
    
    return results

if __name__ == "__main__":
    print("🔍 Quick Backend API Test for Navigation Features")
    print("=" * 50)
    
    results = test_key_endpoints()
    
    passed = sum(1 for _, success, _ in results if success)
    total = len(results)
    
    print(f"\n📊 Results: {passed}/{total} endpoints working")
    
    if passed == total:
        print("✅ All key endpoints are working - proceeding with frontend testing")
        sys.exit(0)
    else:
        print("❌ Some endpoints failed - need to fix backend first")
        sys.exit(1)
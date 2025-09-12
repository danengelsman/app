import requests
import json

def test_local_api():
    # Test local backend directly
    local_url = "http://localhost:8001/api"
    
    print("🔍 Testing Local Backend API...")
    
    try:
        # Test API health
        response = requests.get(f"{local_url}/", timeout=5)
        print(f"API Health: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {response.json()}")
        
        # Test trending topics
        response = requests.get(f"{local_url}/trending-topics", timeout=10)
        print(f"Trending Topics Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            topics = data.get('topics', [])
            print(f"Found {len(topics)} topics")
            
            if len(topics) > 0:
                print("✅ Topics found! Bug appears to be fixed.")
                for i, topic in enumerate(topics[:5]):
                    print(f"  {i+1}. {topic.get('keyword', 'No keyword')} (Score: {topic.get('trend_score', 'N/A')})")
                    print(f"      Search Volume: {topic.get('search_volume', 'N/A')}")
                    print(f"      Competition: {topic.get('competition_level', 'N/A')}")
                    print(f"      Platforms: {topic.get('platforms', [])}")
            else:
                print("❌ No topics found - bug may still exist")
        else:
            print(f"❌ API call failed: {response.text}")
            
        # Test dashboard analytics
        response = requests.get(f"{local_url}/analytics/dashboard", timeout=10)
        print(f"Dashboard Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            topics_count = data.get('trending_topics_this_week', 0)
            print(f"Dashboard shows {topics_count} trending topics this week")
            
            if topics_count > 0:
                print("✅ Dashboard no longer shows 0 topics")
            else:
                print("❌ Dashboard still shows 0 topics")
                
            recent_content = data.get('recent_content', [])
            print(f"Recent content count: {len(recent_content)}")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    test_local_api()
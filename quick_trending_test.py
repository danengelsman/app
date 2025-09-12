import requests
import json

def test_trending_topics():
    base_url = "https://ai-creator-system.preview.emergentagent.com"
    api_url = f"{base_url}/api"
    
    print("🔍 Testing Trending Topics API...")
    
    try:
        # Test API health first
        response = requests.get(f"{api_url}/", timeout=10)
        print(f"API Health: {response.status_code}")
        
        # Test trending topics
        response = requests.get(f"{api_url}/trending-topics", timeout=10)
        print(f"Trending Topics Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            topics = data.get('topics', [])
            print(f"Found {len(topics)} topics")
            
            if len(topics) > 0:
                print("✅ Topics found! Bug appears to be fixed.")
                for i, topic in enumerate(topics[:3]):
                    print(f"  {i+1}. {topic.get('keyword', 'No keyword')} (Score: {topic.get('trend_score', 'N/A')})")
            else:
                print("❌ No topics found - bug may still exist")
        else:
            print(f"❌ API call failed: {response.text}")
            
        # Test dashboard analytics
        response = requests.get(f"{api_url}/analytics/dashboard", timeout=10)
        print(f"Dashboard Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            topics_count = data.get('trending_topics_this_week', 0)
            print(f"Dashboard shows {topics_count} trending topics this week")
            
            if topics_count > 0:
                print("✅ Dashboard no longer shows 0 topics")
            else:
                print("❌ Dashboard still shows 0 topics")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    test_trending_topics()
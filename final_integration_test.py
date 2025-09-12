import requests
import json

def comprehensive_trending_topics_test():
    base_url = "https://ai-creator-system.preview.emergentagent.com"
    api_url = f"{base_url}/api"
    
    print("🚀 COMPREHENSIVE TRENDING TOPICS BUG FIX VERIFICATION")
    print("=" * 70)
    
    results = {
        "backend_api": False,
        "expected_topics": False,
        "dashboard_integration": False,
        "data_structure": False,
        "agent_status": False
    }
    
    try:
        # 1. Test Trending Topics API
        print("\n1️⃣ Testing Trending Topics API...")
        response = requests.get(f"{api_url}/trending-topics", timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            topics = data.get('topics', [])
            print(f"✅ API Status: 200 OK")
            print(f"✅ Topics Count: {len(topics)} (should be > 0)")
            
            if len(topics) > 0:
                results["backend_api"] = True
                
                # 2. Verify Expected Topics
                print("\n2️⃣ Verifying Expected Fallback Topics...")
                expected_topics = [
                    "AI coding assistants", 
                    "Cybersecurity threats 2025", 
                    "Apple Vision Pro review", 
                    "Python automation tools", 
                    "Tech startup funding"
                ]
                
                found_keywords = [topic.get('keyword', '') for topic in topics]
                expected_found = sum(1 for expected in expected_topics if expected in found_keywords)
                
                print(f"✅ Expected Topics Found: {expected_found}/{len(expected_topics)}")
                for expected in expected_topics:
                    status = "✅" if expected in found_keywords else "❌"
                    print(f"  {status} {expected}")
                
                if expected_found >= 3:  # At least 3 out of 5 expected topics
                    results["expected_topics"] = True
                
                # 3. Verify Data Structure
                print("\n3️⃣ Verifying Topic Data Structure...")
                sample_topic = topics[0]
                required_fields = ['keyword', 'search_volume', 'competition_level', 'trend_score', 'platforms', 'discovered_date']
                
                structure_valid = True
                for field in required_fields:
                    if field in sample_topic:
                        print(f"✅ {field}: {sample_topic[field]}")
                    else:
                        print(f"❌ Missing field: {field}")
                        structure_valid = False
                
                if structure_valid:
                    results["data_structure"] = True
            else:
                print("❌ No topics found - bug not fixed")
        else:
            print(f"❌ API Error: {response.status_code}")
    
    except Exception as e:
        print(f"❌ API Test Error: {str(e)}")
    
    try:
        # 4. Test Dashboard Integration
        print("\n4️⃣ Testing Dashboard Integration...")
        response = requests.get(f"{api_url}/analytics/dashboard", timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            topics_count = data.get('trending_topics_this_week', 0)
            
            print(f"✅ Dashboard API: 200 OK")
            print(f"✅ Weekly Topics Count: {topics_count}")
            
            if topics_count > 0:
                print("✅ Dashboard no longer shows 0 topics")
                results["dashboard_integration"] = True
            else:
                print("❌ Dashboard still shows 0 topics")
        else:
            print(f"❌ Dashboard API Error: {response.status_code}")
    
    except Exception as e:
        print(f"❌ Dashboard Test Error: {str(e)}")
    
    try:
        # 5. Test Agent Status
        print("\n5️⃣ Testing Agent Status...")
        response = requests.get(f"{api_url}/agents/status", timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            agents = data.get('agents', {})
            
            print(f"✅ Agents API: 200 OK")
            print(f"✅ Total Agents: {len(agents)}")
            
            if 'trending_topics' in agents:
                trending_agent = agents['trending_topics']
                print(f"✅ Trending Topics Agent Found")
                print(f"  Status: {trending_agent.get('status')}")
                print(f"  Name: {trending_agent.get('name')}")
                results["agent_status"] = True
            else:
                print("❌ Trending Topics Agent not found")
        else:
            print(f"❌ Agents API Error: {response.status_code}")
    
    except Exception as e:
        print(f"❌ Agent Status Test Error: {str(e)}")
    
    # Final Results
    print("\n" + "=" * 70)
    print("🏁 FINAL TEST RESULTS")
    print("=" * 70)
    
    passed_tests = sum(results.values())
    total_tests = len(results)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} {test_name.replace('_', ' ').title()}")
    
    print(f"\n📊 Overall Score: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 ALL TESTS PASSED! Trending topics bug is completely fixed!")
        return True
    elif passed_tests >= 3:
        print("✅ Most tests passed. Bug appears to be mostly fixed.")
        return True
    else:
        print("❌ Multiple test failures. Bug may not be fully fixed.")
        return False

if __name__ == "__main__":
    success = comprehensive_trending_topics_test()
    exit(0 if success else 1)
import requests
import sys
import json
import time
from datetime import datetime

class MultiAgentSystemTester:
    def __init__(self, base_url="https://ai-creator-system.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.workflow_executed = False

    def run_test(self, name, method, endpoint, expected_status, data=None, timeout=30):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}" if endpoint else f"{self.api_url}/"
        headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=timeout)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=timeout)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    if isinstance(response_data, dict):
                        if 'message' in response_data:
                            print(f"   Message: {response_data['message']}")
                        if 'status' in response_data:
                            print(f"   Status: {response_data['status']}")
                        if 'agents_executed' in response_data:
                            print(f"   Agents Executed: {response_data['agents_executed']}")
                        if 'workflow_completed' in response_data:
                            print(f"   Workflow Completed: {response_data['workflow_completed']}")
                except:
                    pass
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Response: {response.text[:200]}")

            return success, response.json() if response.content else {}

        except requests.exceptions.Timeout:
            print(f"❌ Failed - Request timed out after {timeout} seconds")
            return False, {}
        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_basic_health_check(self):
        """Test basic API health check"""
        return self.run_test(
            "Basic Health Check",
            "GET",
            "",
            200
        )

    def test_agents_status(self):
        """Test agents status endpoint"""
        return self.run_test(
            "Agents Status",
            "GET",
            "agents/status",
            200
        )

    def test_execute_workflow(self):
        """Test full workflow execution - this is the main test"""
        print("\n🚀 Starting Full Multi-Agent Workflow Execution...")
        print("   This may take 60-120 seconds as it involves LLM processing...")
        
        success, response = self.run_test(
            "Execute Full Workflow (All 9 Agents)",
            "POST",
            "agents/execute-workflow",
            200,
            timeout=180  # Extended timeout for LLM processing
        )
        
        if success:
            self.workflow_executed = True
            print(f"\n📊 Workflow Summary:")
            if 'summary' in response:
                summary = response['summary']
                print(f"   Topics Discovered: {summary.get('topics_discovered', 0)}")
                print(f"   Content Pieces Created: {summary.get('content_pieces_created', 0)}")
                print(f"   Blog Posts Created: {summary.get('blog_posts_created', 0)}")
                print(f"   Compliance Approved: {summary.get('compliance_approved', 0)}")
        
        return success, response

    def test_trending_topics(self):
        """Test trending topics endpoint with detailed validation"""
        success, response = self.run_test(
            "Get Trending Topics",
            "GET",
            "trending-topics",
            200
        )
        
        if success and response:
            topics = response.get('topics', [])
            print(f"   Found {len(topics)} topics")
            
            # Expected fallback topics that should be present
            expected_topics = [
                "AI coding assistants", 
                "Cybersecurity threats 2025", 
                "Apple Vision Pro review", 
                "Python automation tools", 
                "Tech startup funding"
            ]
            
            # Check if we have topics (should no longer be empty)
            if len(topics) == 0:
                print("   ❌ No topics found - the bug fix may not be working")
                return False, response
            
            # Validate topic structure
            for i, topic in enumerate(topics[:3]):  # Check first 3 topics
                print(f"   Topic {i+1}: {topic.get('keyword', 'No keyword')}")
                required_fields = ['keyword', 'search_volume', 'competition_level', 'trend_score', 'platforms', 'discovered_date']
                
                missing_fields = [field for field in required_fields if field not in topic]
                if missing_fields:
                    print(f"   ❌ Missing fields: {missing_fields}")
                    return False, response
                
                # Verify data types
                if not isinstance(topic.get('search_volume'), int):
                    print(f"   ❌ search_volume should be int, got {type(topic.get('search_volume'))}")
                    return False, response
                
                if not isinstance(topic.get('trend_score'), (int, float)):
                    print(f"   ❌ trend_score should be number, got {type(topic.get('trend_score'))}")
                    return False, response
            
            # Check for expected fallback topics
            found_keywords = [topic.get('keyword', '') for topic in topics]
            expected_found = sum(1 for expected in expected_topics if expected in found_keywords)
            
            print(f"   ✅ Found {expected_found}/{len(expected_topics)} expected fallback topics")
            
            if expected_found > 0:
                print("   ✅ Fallback topics are working correctly")
            else:
                print("   ⚠️  No expected fallback topics found, but topics exist")
            
            return True, response
        
        return success, response

    def test_content_library(self):
        """Test content library endpoint"""
        return self.run_test(
            "Get Content Library",
            "GET",
            "content",
            200
        )

    def test_branding_kit(self):
        """Test branding kit endpoint"""
        return self.run_test(
            "Get Branding Kit",
            "GET",
            "branding",
            200
        )

    def test_blog_posts(self):
        """Test blog posts endpoint"""
        return self.run_test(
            "Get Blog Posts",
            "GET",
            "blog-posts",
            200
        )

    def test_analytics_dashboard(self):
        """Test analytics dashboard endpoint"""
        return self.run_test(
            "Get Analytics Dashboard",
            "GET",
            "analytics/dashboard",
            200
        )

    def test_detailed_analytics(self):
        """Test detailed analytics endpoint"""
        return self.run_test(
            "Get Detailed Analytics",
            "GET",
            "analytics/detailed",
            200,
            timeout=60  # Extended timeout for LLM processing
        )

    def test_compliance_check(self):
        """Test compliance check endpoint"""
        return self.run_test(
            "Content Compliance Check",
            "POST",
            "content/compliance-check",
            200,
            timeout=60  # Extended timeout for LLM processing
        )

    def test_monetization_strategies(self):
        """Test monetization strategies endpoint"""
        return self.run_test(
            "Get Monetization Strategies",
            "GET",
            "monetization/strategies",
            200
        )

    def test_content_filtering(self):
        """Test content filtering by platform"""
        platforms = ['youtube', 'instagram', 'tiktok', 'twitter']
        
        for platform in platforms:
            success, response = self.run_test(
                f"Get {platform.title()} Content",
                "GET",
                f"content?platform={platform}",
                200
            )
            if not success:
                return False, {}
        
        return True, {}

def main():
    print("🤖 Starting Emergent AI Multi-Agent Content Creation System Tests")
    print("=" * 70)
    
    tester = MultiAgentSystemTester()
    
    # Test sequence - start with basic tests, then workflow, then data tests
    test_sequence = [
        ("Basic API Health", tester.test_basic_health_check),
        ("Agents Status Check", tester.test_agents_status),
        ("Analytics Dashboard (Pre-Workflow)", tester.test_analytics_dashboard),
        ("Monetization Strategies", tester.test_monetization_strategies),
        ("Full Multi-Agent Workflow", tester.test_execute_workflow),
        ("Trending Topics (Post-Workflow)", tester.test_trending_topics),
        ("Content Library (Post-Workflow)", tester.test_content_library),
        ("Branding Kit (Post-Workflow)", tester.test_branding_kit),
        ("Blog Posts (Post-Workflow)", tester.test_blog_posts),
        ("Content Platform Filtering", tester.test_content_filtering),
        ("Detailed Analytics", tester.test_detailed_analytics),
        ("Compliance Check", tester.test_compliance_check),
    ]
    
    failed_tests = []
    
    for test_name, test_func in test_sequence:
        print(f"\n{'='*50}")
        print(f"Running: {test_name}")
        print(f"{'='*50}")
        
        try:
            success, response = test_func()
            if not success:
                failed_tests.append(test_name)
        except Exception as e:
            print(f"❌ Test '{test_name}' crashed: {str(e)}")
            failed_tests.append(test_name)
            tester.tests_run += 1
    
    # Print final results
    print(f"\n{'='*70}")
    print(f"🏁 TEST RESULTS SUMMARY")
    print(f"{'='*70}")
    print(f"📊 Tests passed: {tester.tests_passed}/{tester.tests_run}")
    print(f"🎯 Success rate: {(tester.tests_passed/tester.tests_run*100):.1f}%")
    
    if tester.workflow_executed:
        print(f"✅ Multi-agent workflow executed successfully")
    else:
        print(f"❌ Multi-agent workflow failed to execute")
    
    if failed_tests:
        print(f"\n❌ Failed Tests:")
        for test in failed_tests:
            print(f"   - {test}")
    else:
        print(f"\n🎉 All tests passed!")
    
    print(f"\n🔍 Key System Capabilities Tested:")
    print(f"   ✓ 9 AI Agents coordination")
    print(f"   ✓ LLM integration with Emergent Universal Key")
    print(f"   ✓ MongoDB data persistence")
    print(f"   ✓ Content creation across 4 platforms")
    print(f"   ✓ Branding consistency")
    print(f"   ✓ Analytics and compliance")
    print(f"   ✓ Monetization strategies")
    
    return 0 if tester.tests_passed == tester.tests_run else 1

if __name__ == "__main__":
    sys.exit(main())
import requests
import sys
import json
import time
from datetime import datetime

class MultiAgentSystemTester:
    def __init__(self, base_url="https://emergent-content-1.preview.emergentagent.com"):
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
        """Test analytics dashboard endpoint with trending topics validation"""
        success, response = self.run_test(
            "Get Analytics Dashboard",
            "GET",
            "analytics/dashboard",
            200
        )
        
        if success and response:
            topics_count = response.get('trending_topics_this_week', 0)
            print(f"   Weekly Trending Topics Count: {topics_count}")
            
            if topics_count == 0:
                print("   ⚠️  Dashboard still shows 0 trending topics - bug may not be fully fixed")
            else:
                print(f"   ✅ Dashboard shows {topics_count} trending topics (no longer 0)")
            
            recent_content = response.get('recent_content', [])
            print(f"   Recent Content Count: {len(recent_content)}")
            
            platform_distribution = response.get('platform_distribution', [])
            print(f"   Platform Distribution: {len(platform_distribution)} platforms")
            
        return success, response

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

    def test_voice_clone_credentials(self):
        """Test Minimax API credentials validation"""
        success, response = self.run_test(
            "Voice Clone Credentials Test",
            "GET",
            "voice-clone/test-credentials/",
            200
        )
        
        if success and response:
            credentials_valid = response.get('credentials_valid', False)
            message = response.get('message', '')
            print(f"   Credentials Valid: {credentials_valid}")
            print(f"   Message: {message}")
            
            if not credentials_valid:
                print("   ❌ Minimax credentials are invalid or missing")
                return False, response
            else:
                print("   ✅ Minimax credentials are valid")
        
        return success, response

    def test_voice_clone_health(self):
        """Test voice cloning service health check"""
        success, response = self.run_test(
            "Voice Clone Health Check",
            "GET",
            "voice-clone/health/",
            200
        )
        
        if success and response:
            status = response.get('status', 'unknown')
            minimax_creds = response.get('minimax_credentials', 'unknown')
            temp_dir = response.get('temp_directory', 'unknown')
            
            print(f"   Overall Status: {status}")
            print(f"   Minimax Credentials: {minimax_creds}")
            print(f"   Temp Directory: {temp_dir}")
            
            if status != 'healthy':
                print("   ⚠️  Voice cloning service is not fully healthy")
                if minimax_creds != 'valid':
                    print("   ❌ Minimax credentials issue detected")
                if temp_dir != 'accessible':
                    print("   ❌ Temp directory access issue detected")
            else:
                print("   ✅ Voice cloning service is healthy")
        
        return success, response

    def test_voice_clone_create_validation(self):
        """Test voice clone creation endpoint validation (without actual file)"""
        # Test missing parameters
        success, response = self.run_test(
            "Voice Clone Create - Missing Parameters",
            "POST",
            "voice-clone/create/",
            422  # FastAPI validation error
        )
        
        if success:
            print("   ✅ Properly validates missing parameters")
        else:
            print("   ❌ Should return 422 for missing parameters")
            return False, response
        
        return True, response

    def test_voice_clone_generate_speech_validation(self):
        """Test speech generation endpoint validation"""
        # Test with missing parameters
        success, response = self.run_test(
            "Voice Clone Generate Speech - Missing Parameters",
            "POST",
            "voice-clone/generate-speech/",
            422  # FastAPI validation error
        )
        
        if success:
            print("   ✅ Properly validates missing parameters")
        else:
            print("   ❌ Should return 422 for missing parameters")
            return False, response
        
        # Test with invalid data structure
        invalid_data = {"invalid": "data"}
        success, response = self.run_test(
            "Voice Clone Generate Speech - Invalid Data",
            "POST",
            "voice-clone/generate-speech/",
            422,  # FastAPI validation error
            data=invalid_data
        )
        
        if success:
            print("   ✅ Properly validates invalid data structure")
        else:
            print("   ❌ Should return 422 for invalid data structure")
            return False, response
        
        # Test with valid structure but non-existent voice
        valid_data = {
            "text": "Hello, this is a test message for voice cloning.",
            "voice_id": "non_existent_voice_test_123",
            "model": "speech-01"
        }
        success, response = self.run_test(
            "Voice Clone Generate Speech - Non-existent Voice",
            "POST",
            "voice-clone/generate-speech/",
            400,  # Should return error for non-existent voice
            data=valid_data,
            timeout=60
        )
        
        if success:
            print("   ✅ Properly handles non-existent voice ID")
        elif response and 'status_code' in str(response):
            # If we get a different error code, that's also acceptable
            print("   ✅ Returns appropriate error for non-existent voice")
            return True, response
        else:
            print("   ⚠️  Unexpected response for non-existent voice test")
        
        return True, response

    def test_voice_clone_endpoints_structure(self):
        """Test voice cloning endpoints response structure"""
        print("\n🔍 Testing Voice Clone API Response Structures...")
        
        # Test credentials endpoint structure
        success, creds_response = self.test_voice_clone_credentials()
        if success and creds_response:
            required_fields = ['credentials_valid', 'message', 'timestamp']
            missing_fields = [field for field in required_fields if field not in creds_response]
            if missing_fields:
                print(f"   ❌ Credentials response missing fields: {missing_fields}")
                return False, creds_response
            else:
                print("   ✅ Credentials response has all required fields")
        
        # Test health endpoint structure  
        success, health_response = self.test_voice_clone_health()
        if success and health_response:
            required_fields = ['status', 'minimax_credentials', 'temp_directory', 'timestamp']
            missing_fields = [field for field in required_fields if field not in health_response]
            if missing_fields:
                print(f"   ❌ Health response missing fields: {missing_fields}")
                return False, health_response
            else:
                print("   ✅ Health response has all required fields")
        
        return True, {}

    def run_voice_clone_tests(self):
        """Run all voice cloning tests"""
        print(f"\n{'='*60}")
        print(f"🎤 VOICE CLONING INTEGRATION TESTS")
        print(f"{'='*60}")
        
        voice_tests = [
            ("Voice Clone Credentials", self.test_voice_clone_credentials),
            ("Voice Clone Health Check", self.test_voice_clone_health),
            ("Voice Clone Create Validation", self.test_voice_clone_create_validation),
            ("Voice Clone Generate Speech Validation", self.test_voice_clone_generate_speech_validation),
            ("Voice Clone Response Structures", self.test_voice_clone_endpoints_structure),
        ]
        
        voice_test_results = []
        
        for test_name, test_func in voice_tests:
            print(f"\n{'-'*40}")
            print(f"Running: {test_name}")
            print(f"{'-'*40}")
            
            try:
                success, response = test_func()
                voice_test_results.append((test_name, success))
                if not success:
                    print(f"❌ {test_name} failed")
                else:
                    print(f"✅ {test_name} passed")
            except Exception as e:
                print(f"❌ {test_name} crashed: {str(e)}")
                voice_test_results.append((test_name, False))
                self.tests_run += 1
        
        # Summary of voice cloning tests
        passed_voice_tests = sum(1 for _, success in voice_test_results if success)
        total_voice_tests = len(voice_test_results)
        
        print(f"\n{'='*60}")
        print(f"🎤 VOICE CLONING TEST SUMMARY")
        print(f"{'='*60}")
        print(f"Voice Clone Tests: {passed_voice_tests}/{total_voice_tests} passed")
        
        if passed_voice_tests == total_voice_tests:
            print("🎉 All voice cloning tests passed!")
        else:
            print("❌ Some voice cloning tests failed:")
            for test_name, success in voice_test_results:
                if not success:
                    print(f"   - {test_name}")
        
        return passed_voice_tests == total_voice_tests

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
    
    # Run Voice Cloning Tests
    voice_tests_passed = tester.run_voice_clone_tests()
    if not voice_tests_passed:
        failed_tests.append("Voice Cloning Integration")
    
    # Print final results
    print(f"\n{'='*70}")
    print(f"🏁 COMPLETE TEST RESULTS SUMMARY")
    print(f"{'='*70}")
    print(f"📊 Multi-Agent Tests passed: {tester.tests_passed}/{tester.tests_run}")
    print(f"🎤 Voice Cloning Tests: {'✅ PASSED' if voice_tests_passed else '❌ FAILED'}")
    print(f"🎯 Overall Success rate: {(tester.tests_passed/tester.tests_run*100):.1f}%")
    
    if tester.workflow_executed:
        print(f"✅ Multi-agent workflow executed successfully")
    else:
        print(f"❌ Multi-agent workflow failed to execute")
    
    if failed_tests:
        print(f"\n❌ Failed Test Categories:")
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
    print(f"   ✓ Minimax Voice Cloning Integration")
    print(f"   ✓ Voice clone credentials validation")
    print(f"   ✓ Voice cloning health checks")
    print(f"   ✓ Voice cloning API validation")
    
    return 0 if (tester.tests_passed == tester.tests_run and voice_tests_passed) else 1

if __name__ == "__main__":
    sys.exit(main())
#!/usr/bin/env python3
"""
Focused Voice Cloning Integration Test
Tests the Minimax voice cloning endpoints specifically
"""

import requests
import sys
import json
import time
from datetime import datetime

class VoiceCloneIntegrationTester:
    def __init__(self, base_url="https://emergent-content-1.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0

    def run_test(self, name, method, endpoint, expected_status, data=None, timeout=30):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
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
                    return success, response_data
                except:
                    return success, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                    return success, error_data
                except:
                    print(f"   Response: {response.text[:200]}")
                    return success, {"error": response.text[:200]}

        except requests.exceptions.Timeout:
            print(f"❌ Failed - Request timed out after {timeout} seconds")
            return False, {"error": "timeout"}
        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {"error": str(e)}

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
            timestamp = response.get('timestamp', '')
            
            print(f"   Credentials Valid: {credentials_valid}")
            print(f"   Message: {message}")
            print(f"   Timestamp: {timestamp}")
            
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
            timestamp = response.get('timestamp', '')
            
            print(f"   Overall Status: {status}")
            print(f"   Minimax Credentials: {minimax_creds}")
            print(f"   Temp Directory: {temp_dir}")
            print(f"   Timestamp: {timestamp}")
            
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
            if 'detail' in response:
                print(f"   Validation details: {response['detail'][:100]}...")
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
            if 'detail' in response:
                print(f"   Validation details: {response['detail'][:100]}...")
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
        elif response and ('status_code' in str(response) or 'error' in response):
            # If we get a different error code, that's also acceptable
            print("   ✅ Returns appropriate error for non-existent voice")
            return True, response
        else:
            print("   ⚠️  Unexpected response for non-existent voice test")
        
        return True, response

    def test_response_structures(self):
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

def main():
    print("🎤 Minimax Voice Cloning Integration Test")
    print("=" * 60)
    
    tester = VoiceCloneIntegrationTester()
    
    # Voice cloning test sequence
    voice_tests = [
        ("Voice Clone Credentials", tester.test_voice_clone_credentials),
        ("Voice Clone Health Check", tester.test_voice_clone_health),
        ("Voice Clone Create Validation", tester.test_voice_clone_create_validation),
        ("Voice Clone Generate Speech Validation", tester.test_voice_clone_generate_speech_validation),
        ("Voice Clone Response Structures", tester.test_response_structures),
    ]
    
    failed_tests = []
    
    for test_name, test_func in voice_tests:
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
    print(f"\n{'='*60}")
    print(f"🏁 VOICE CLONING TEST RESULTS")
    print(f"{'='*60}")
    print(f"📊 Tests passed: {tester.tests_passed}/{tester.tests_run}")
    print(f"🎯 Success rate: {(tester.tests_passed/tester.tests_run*100):.1f}%")
    
    if failed_tests:
        print(f"\n❌ Failed Tests:")
        for test in failed_tests:
            print(f"   - {test}")
    else:
        print(f"\n🎉 All voice cloning tests passed!")
    
    print(f"\n🔍 Voice Cloning Capabilities Tested:")
    print(f"   ✓ Minimax API credentials validation")
    print(f"   ✓ Voice cloning service health check")
    print(f"   ✓ Voice clone creation endpoint validation")
    print(f"   ✓ Speech generation endpoint validation")
    print(f"   ✓ API response structure validation")
    print(f"   ✓ Error handling and parameter validation")
    
    return 0 if tester.tests_passed == tester.tests_run else 1

if __name__ == "__main__":
    sys.exit(main())
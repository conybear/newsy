#!/usr/bin/env python3
"""
Basic Functionality Testing for Acta Diurna Application
Tests core authentication and invitation system functionality as requested in review
"""

import requests
import json
import time
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = "https://e4f87101-35d9-4339-9777-88089f139507.preview.emergentagent.com/api"

class BasicBackendTester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.user_id = None
        self.test_results = []
        
    def log_test(self, test_name, success, message="", details=None):
        """Log test results"""
        result = {
            "test": test_name,
            "success": success,
            "message": message,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        if message:
            print(f"   {message}")
        if not success and details:
            print(f"   Details: {details}")
        print()

    def test_health_check(self):
        """Test /api/health endpoint to verify backend is running"""
        try:
            response = self.session.get(f"{BACKEND_URL}/health")
            if response.status_code == 200:
                data = response.json()
                self.log_test("Health Check", True, 
                    f"Status: {data.get('status')}, Current Week: {data.get('current_week')}")
                return True
            else:
                self.log_test("Health Check", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Health Check", False, f"Exception: {str(e)}")
            return False

    def test_user_registration(self):
        """Register a new test user with specified credentials"""
        try:
            user_data = {
                "email": "test@actadiurna.com",
                "password": "TestPass123!",
                "full_name": "Test User"
            }
            
            response = self.session.post(f"{BACKEND_URL}/auth/register", json=user_data)
            
            if response.status_code == 200:
                data = response.json()
                if "access_token" in data:
                    self.auth_token = data["access_token"]
                    self.session.headers.update({"Authorization": f"Bearer {self.auth_token}"})
                    self.log_test("User Registration", True, 
                        f"User registered successfully: {data['user']['full_name']} ({data['user']['email']})")
                    return True
                else:
                    self.log_test("User Registration", False, "No access token in response", data)
                    return False
            elif response.status_code == 400 and "already registered" in response.text:
                # User already exists, try to login instead
                self.log_test("User Registration", True, "User already exists, proceeding to login test")
                return True
            else:
                self.log_test("User Registration", False, f"Status code: {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("User Registration", False, f"Exception: {str(e)}")
            return False

    def test_user_login(self):
        """Login with the registered user"""
        try:
            login_data = {
                "email": "test@actadiurna.com",
                "password": "TestPass123!"
            }
            
            response = self.session.post(f"{BACKEND_URL}/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                if "access_token" in data:
                    self.auth_token = data["access_token"]
                    self.session.headers.update({"Authorization": f"Bearer {self.auth_token}"})
                    self.log_test("User Login", True, 
                        f"Login successful: {data['user']['full_name']} ({data['user']['email']})")
                    return True
                else:
                    self.log_test("User Login", False, "No access token in response", data)
                    return False
            else:
                self.log_test("User Login", False, f"Status code: {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("User Login", False, f"Exception: {str(e)}")
            return False

    def test_get_current_user_info(self):
        """Get current user information"""
        try:
            if not self.auth_token:
                self.log_test("Get Current User Info", False, "No auth token available")
                return False
                
            response = self.session.get(f"{BACKEND_URL}/users/me")
            
            if response.status_code == 200:
                data = response.json()
                if "id" in data and "email" in data and "full_name" in data:
                    self.user_id = data["id"]
                    self.log_test("Get Current User Info", True, 
                        f"User info retrieved: {data['full_name']} ({data['email']}) - ID: {data['id']}")
                    return True
                else:
                    self.log_test("Get Current User Info", False, "Invalid user data structure", data)
                    return False
            else:
                self.log_test("Get Current User Info", False, f"Status code: {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("Get Current User Info", False, f"Exception: {str(e)}")
            return False

    def test_send_invitation(self):
        """Test invitation system by sending an invitation"""
        try:
            if not self.auth_token:
                self.log_test("Send Invitation", False, "No auth token available")
                return False
                
            invitation_data = {
                "email": "friend@actadiurna.com"
            }
            
            response = self.session.post(f"{BACKEND_URL}/invitations/send", json=invitation_data)
            
            if response.status_code == 200:
                data = response.json()
                if "message" in data:
                    self.log_test("Send Invitation", True, data["message"])
                    return True
                else:
                    self.log_test("Send Invitation", False, "Invalid response structure", data)
                    return False
            elif response.status_code == 400 and "Already invited" in response.text:
                self.log_test("Send Invitation", True, "Invitation already sent (expected behavior)")
                return True
            else:
                self.log_test("Send Invitation", False, f"Status code: {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("Send Invitation", False, f"Exception: {str(e)}")
            return False

    def test_get_sent_invitations(self):
        """Test fetching sent invitations"""
        try:
            if not self.auth_token:
                self.log_test("Get Sent Invitations", False, "No auth token available")
                return False
                
            response = self.session.get(f"{BACKEND_URL}/invitations/sent")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_test("Get Sent Invitations", True, 
                        f"Retrieved {len(data)} sent invitations")
                    for invitation in data:
                        print(f"   - To: {invitation.get('to_email')}, Status: {invitation.get('status')}")
                    return True
                else:
                    self.log_test("Get Sent Invitations", False, "Response is not a list", data)
                    return False
            else:
                self.log_test("Get Sent Invitations", False, f"Status code: {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("Get Sent Invitations", False, f"Exception: {str(e)}")
            return False

    def test_get_received_invitations(self):
        """Test fetching received invitations"""
        try:
            if not self.auth_token:
                self.log_test("Get Received Invitations", False, "No auth token available")
                return False
                
            response = self.session.get(f"{BACKEND_URL}/invitations/received")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_test("Get Received Invitations", True, 
                        f"Retrieved {len(data)} received invitations")
                    for invitation in data:
                        print(f"   - From: {invitation.get('from_user_email')}, Status: {invitation.get('status')}")
                    return True
                else:
                    self.log_test("Get Received Invitations", False, "Response is not a list", data)
                    return False
            else:
                self.log_test("Get Received Invitations", False, f"Status code: {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("Get Received Invitations", False, f"Exception: {str(e)}")
            return False

    def run_basic_tests(self):
        """Run all basic functionality tests as requested in review"""
        print("🚀 Starting Basic Functionality Testing for Acta Diurna Application")
        print("=" * 70)
        print("Testing core foundation: Authentication system, User management, Basic invitation system")
        print()
        
        # Test sequence as requested in review
        tests = [
            ("Health Check", self.test_health_check),
            ("User Registration", self.test_user_registration),
            ("User Login", self.test_user_login),
            ("User Info", self.test_get_current_user_info),
            ("Send Invitation", self.test_send_invitation),
            ("Invitation Management - Sent", self.test_get_sent_invitations),
            ("Invitation Management - Received", self.test_get_received_invitations),
        ]
        
        passed = 0
        failed = 0
        
        for test_name, test_func in tests:
            try:
                if test_func():
                    passed += 1
                else:
                    failed += 1
            except Exception as e:
                print(f"❌ CRITICAL ERROR in {test_name}: {str(e)}")
                failed += 1
            
            # Small delay between tests
            time.sleep(0.5)
        
        print("=" * 70)
        print(f"📊 BASIC FUNCTIONALITY TEST SUMMARY")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"📈 Success Rate: {(passed/(passed+failed)*100):.1f}%")
        
        return passed, failed, self.test_results

if __name__ == "__main__":
    tester = BasicBackendTester()
    passed, failed, results = tester.run_basic_tests()
    
    # Save detailed results
    with open('/app/basic_test_results.json', 'w') as f:
        json.dump({
            "summary": {
                "passed": passed,
                "failed": failed,
                "success_rate": passed/(passed+failed)*100 if (passed+failed) > 0 else 0
            },
            "detailed_results": results
        }, f, indent=2)
    
    print(f"\n📄 Detailed results saved to: /app/basic_test_results.json")
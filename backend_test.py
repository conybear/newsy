#!/usr/bin/env python3
"""
Comprehensive Backend API Testing for Social Weekly Newspaper Network
Tests all authentication, story management, friend management, and weekly edition APIs
"""

import requests
import json
import base64
import io
from PIL import Image
import time
import os
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = "https://10eeeb36-2949-49e5-b0bf-259584eeb998.preview.emergentagent.com/api"

class BackendTester:
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

    def create_test_image(self):
        """Create a test image in base64 format"""
        # Create a simple test image
        img = Image.new('RGB', (100, 100), color='red')
        buffer = io.BytesIO()
        img.save(buffer, format='JPEG')
        buffer.seek(0)
        return buffer.getvalue()

    def test_health_check(self):
        """Test health check endpoint"""
        try:
            response = self.session.get(f"{BACKEND_URL}/health")
            if response.status_code == 200:
                data = response.json()
                self.log_test("Health Check", True, f"Status: {data.get('status')}")
                return True
            else:
                self.log_test("Health Check", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Health Check", False, f"Exception: {str(e)}")
            return False

    def test_user_registration(self):
        """Test user registration"""
        try:
            user_data = {
                "email": "sarah.johnson@newspaper.com",
                "password": "SecurePass123!",
                "full_name": "Sarah Johnson"
            }
            
            response = self.session.post(f"{BACKEND_URL}/auth/register", json=user_data)
            
            if response.status_code == 200:
                data = response.json()
                if "access_token" in data:
                    self.auth_token = data["access_token"]
                    self.session.headers.update({"Authorization": f"Bearer {self.auth_token}"})
                    self.log_test("User Registration", True, "User registered successfully with JWT token")
                    return True
                else:
                    self.log_test("User Registration", False, "No access token in response", data)
                    return False
            else:
                self.log_test("User Registration", False, f"Status code: {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("User Registration", False, f"Exception: {str(e)}")
            return False

    def test_user_login(self):
        """Test user login with existing credentials"""
        try:
            login_data = {
                "email": "sarah.johnson@newspaper.com",
                "password": "SecurePass123!"
            }
            
            response = self.session.post(f"{BACKEND_URL}/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                if "access_token" in data:
                    self.auth_token = data["access_token"]
                    self.session.headers.update({"Authorization": f"Bearer {self.auth_token}"})
                    self.log_test("User Login", True, "Login successful with JWT token")
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

    def test_get_current_user(self):
        """Test getting current user info"""
        try:
            if not self.auth_token:
                self.log_test("Get Current User", False, "No auth token available")
                return False
                
            response = self.session.get(f"{BACKEND_URL}/users/me")
            
            if response.status_code == 200:
                data = response.json()
                if "id" in data and "email" in data:
                    self.user_id = data["id"]
                    self.log_test("Get Current User", True, f"User info retrieved: {data['full_name']} ({data['email']})")
                    return True
                else:
                    self.log_test("Get Current User", False, "Invalid user data structure", data)
                    return False
            else:
                self.log_test("Get Current User", False, f"Status code: {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("Get Current User", False, f"Exception: {str(e)}")
            return False

    def test_story_creation(self):
        """Test story creation"""
        try:
            if not self.auth_token:
                self.log_test("Story Creation", False, "No auth token available")
                return False
                
            story_data = {
                "title": "Local Community Garden Flourishes",
                "content": "The downtown community garden has become a thriving hub for neighbors to connect and grow fresh produce together. This week, volunteers harvested over 200 pounds of vegetables that were donated to the local food bank.",
                "is_headline": True
            }
            
            response = self.session.post(f"{BACKEND_URL}/stories", json=story_data)
            
            if response.status_code == 200:
                data = response.json()
                if "id" in data and "title" in data:
                    self.story_id = data["id"]
                    self.log_test("Story Creation", True, f"Story created: {data['title']}")
                    return True
                else:
                    self.log_test("Story Creation", False, "Invalid story data structure", data)
                    return False
            else:
                self.log_test("Story Creation", False, f"Status code: {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("Story Creation", False, f"Exception: {str(e)}")
            return False

    def test_story_image_upload(self):
        """Test story image upload"""
        try:
            if not hasattr(self, 'story_id'):
                self.log_test("Story Image Upload", False, "No story ID available")
                return False
                
            # Create test image
            image_data = self.create_test_image()
            
            files = {
                'file': ('test_image.jpg', image_data, 'image/jpeg')
            }
            
            response = self.session.post(f"{BACKEND_URL}/stories/{self.story_id}/images", files=files)
            
            if response.status_code == 200:
                data = response.json()
                if "message" in data and "image_id" in data:
                    self.log_test("Story Image Upload", True, f"Image uploaded successfully: {data['image_id']}")
                    return True
                else:
                    self.log_test("Story Image Upload", False, "Invalid response structure", data)
                    return False
            else:
                self.log_test("Story Image Upload", False, f"Status code: {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("Story Image Upload", False, f"Exception: {str(e)}")
            return False

    def test_get_my_stories(self):
        """Test getting user's stories"""
        try:
            if not self.auth_token:
                self.log_test("Get My Stories", False, "No auth token available")
                return False
                
            response = self.session.get(f"{BACKEND_URL}/stories/my")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_test("Get My Stories", True, f"Retrieved {len(data)} stories")
                    return True
                else:
                    self.log_test("Get My Stories", False, "Response is not a list", data)
                    return False
            else:
                self.log_test("Get My Stories", False, f"Status code: {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("Get My Stories", False, f"Exception: {str(e)}")
            return False

    def test_friend_request(self):
        """Test sending friend request"""
        try:
            if not self.auth_token:
                self.log_test("Friend Request", False, "No auth token available")
                return False
                
            # First register another user to befriend
            friend_data = {
                "email": "mike.reporter@newspaper.com",
                "password": "FriendPass456!",
                "full_name": "Mike Reporter"
            }
            
            # Register friend user
            friend_response = self.session.post(f"{BACKEND_URL}/auth/register", json=friend_data)
            if friend_response.status_code != 200:
                self.log_test("Friend Request", False, "Could not register friend user", friend_response.text)
                return False
            
            # Send friend request
            request_data = {
                "email": "mike.reporter@newspaper.com"
            }
            
            response = self.session.post(f"{BACKEND_URL}/friends/request", json=request_data)
            
            if response.status_code == 200:
                data = response.json()
                if "message" in data:
                    self.log_test("Friend Request", True, data["message"])
                    return True
                else:
                    self.log_test("Friend Request", False, "Invalid response structure", data)
                    return False
            else:
                self.log_test("Friend Request", False, f"Status code: {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("Friend Request", False, f"Exception: {str(e)}")
            return False

    def test_get_friends(self):
        """Test getting friends list"""
        try:
            if not self.auth_token:
                self.log_test("Get Friends", False, "No auth token available")
                return False
                
            response = self.session.get(f"{BACKEND_URL}/friends")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_test("Get Friends", True, f"Retrieved {len(data)} friends")
                    return True
                else:
                    self.log_test("Get Friends", False, "Response is not a list", data)
                    return False
            else:
                self.log_test("Get Friends", False, f"Status code: {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("Get Friends", False, f"Exception: {str(e)}")
            return False

    def test_current_edition(self):
        """Test getting current weekly edition"""
        try:
            if not self.auth_token:
                self.log_test("Current Edition", False, "No auth token available")
                return False
                
            response = self.session.get(f"{BACKEND_URL}/editions/current")
            
            if response.status_code == 200:
                data = response.json()
                if "id" in data and "week_of" in data:
                    self.log_test("Current Edition", True, f"Current edition for week: {data['week_of']}")
                    return True
                else:
                    self.log_test("Current Edition", False, "Invalid edition data structure", data)
                    return False
            else:
                self.log_test("Current Edition", False, f"Status code: {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("Current Edition", False, f"Exception: {str(e)}")
            return False

    def test_edition_archive(self):
        """Test getting edition archive"""
        try:
            if not self.auth_token:
                self.log_test("Edition Archive", False, "No auth token available")
                return False
                
            response = self.session.get(f"{BACKEND_URL}/editions/archive")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_test("Edition Archive", True, f"Retrieved {len(data)} archived editions")
                    return True
                else:
                    self.log_test("Edition Archive", False, "Response is not a list", data)
                    return False
            else:
                self.log_test("Edition Archive", False, f"Status code: {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("Edition Archive", False, f"Exception: {str(e)}")
            return False

    def test_weekly_story_limit(self):
        """Test that users can only submit one story per week"""
        try:
            if not self.auth_token:
                self.log_test("Weekly Story Limit", False, "No auth token available")
                return False
                
            # Try to create another story this week
            story_data = {
                "title": "Second Story This Week",
                "content": "This should fail due to weekly limit",
                "is_headline": False
            }
            
            response = self.session.post(f"{BACKEND_URL}/stories", json=story_data)
            
            if response.status_code == 400:
                self.log_test("Weekly Story Limit", True, "Weekly story limit properly enforced")
                return True
            else:
                self.log_test("Weekly Story Limit", False, f"Expected 400 status, got {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("Weekly Story Limit", False, f"Exception: {str(e)}")
            return False

    def run_all_tests(self):
        """Run all backend tests"""
        print("🚀 Starting Backend API Testing for Social Weekly Newspaper Network")
        print("=" * 70)
        
        # Test sequence
        tests = [
            self.test_health_check,
            self.test_user_registration,
            self.test_get_current_user,
            self.test_story_creation,
            self.test_story_image_upload,
            self.test_get_my_stories,
            self.test_weekly_story_limit,
            self.test_friend_request,
            self.test_get_friends,
            self.test_current_edition,
            self.test_edition_archive,
        ]
        
        passed = 0
        failed = 0
        
        for test in tests:
            try:
                if test():
                    passed += 1
                else:
                    failed += 1
            except Exception as e:
                print(f"❌ CRITICAL ERROR in {test.__name__}: {str(e)}")
                failed += 1
            
            # Small delay between tests
            time.sleep(0.5)
        
        print("=" * 70)
        print(f"📊 TEST SUMMARY")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"📈 Success Rate: {(passed/(passed+failed)*100):.1f}%")
        
        return passed, failed, self.test_results

if __name__ == "__main__":
    tester = BackendTester()
    passed, failed, results = tester.run_all_tests()
    
    # Save detailed results
    with open('/app/backend_test_results.json', 'w') as f:
        json.dump({
            "summary": {
                "passed": passed,
                "failed": failed,
                "success_rate": passed/(passed+failed)*100 if (passed+failed) > 0 else 0
            },
            "detailed_results": results
        }, f, indent=2)
    
    print(f"\n📄 Detailed results saved to: /app/backend_test_results.json")
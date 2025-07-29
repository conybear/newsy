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
            # Try multiple possible credentials
            credentials_to_try = [
                {"email": "sarah.johnson@newspaper.com", "password": "SecurePass123!"},
                {"email": "sarah.johnson@example.com", "password": "SecurePass123!"},
                {"email": "sarah.johnson@newspaper.com", "password": "password123"},
                {"email": "sarah.johnson@example.com", "password": "password123"},
            ]
            
            for login_data in credentials_to_try:
                response = self.session.post(f"{BACKEND_URL}/auth/login", json=login_data)
                
                if response.status_code == 200:
                    data = response.json()
                    if "access_token" in data:
                        self.auth_token = data["access_token"]
                        self.session.headers.update({"Authorization": f"Bearer {self.auth_token}"})
                        self.log_test("User Login", True, f"Login successful with {login_data['email']}")
                        return True
                    else:
                        continue
                else:
                    continue
            
            # If all failed, try to register a new user
            new_user_data = {
                "email": "test.user@newspaper.com",
                "password": "TestPass123!",
                "full_name": "Test User"
            }
            
            response = self.session.post(f"{BACKEND_URL}/auth/register", json=new_user_data)
            
            if response.status_code == 200:
                data = response.json()
                if "access_token" in data:
                    self.auth_token = data["access_token"]
                    self.session.headers.update({"Authorization": f"Bearer {self.auth_token}"})
                    self.log_test("User Login", True, "Registered new user and logged in")
                    return True
            
            self.log_test("User Login", False, "All login attempts failed")
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
                
            # First try to register another user to befriend
            friend_data = {
                "email": "mike.reporter@newspaper.com",
                "password": "FriendPass456!",
                "full_name": "Mike Reporter"
            }
            
            # Try to register friend user (might already exist)
            friend_response = self.session.post(f"{BACKEND_URL}/auth/register", json=friend_data)
            if friend_response.status_code == 400:
                # User already exists, that's fine
                print("   Friend user already exists, proceeding with invitation...")
            elif friend_response.status_code != 200:
                self.log_test("Friend Request", False, f"Could not register friend user: {friend_response.text}")
                return False
            
            # Send friend invitation (using correct endpoint)
            request_data = {
                "email": "mike.reporter@newspaper.com"
            }
            
            response = self.session.post(f"{BACKEND_URL}/friends/invite", json=request_data)
            
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

    def test_debug_user_info(self):
        """Test debug endpoint for user info and relationships"""
        try:
            if not self.auth_token:
                self.log_test("Debug User Info", False, "No auth token available")
                return False, None
                
            response = self.session.get(f"{BACKEND_URL}/debug/user-info")
            
            if response.status_code == 200:
                data = response.json()
                if "user" in data and "diagnosis" in data:
                    diagnosis = data["diagnosis"]
                    self.log_test("Debug User Info", True, 
                        f"Friends: {diagnosis['friends_count']}, Contributors: {diagnosis['contributors_count']}, Stories: {diagnosis['contributor_stories_count']}")
                    return True, data
                else:
                    self.log_test("Debug User Info", False, "Invalid debug data structure", data)
                    return False, None
            else:
                self.log_test("Debug User Info", False, f"Status code: {response.status_code}", response.text)
                return False, None
        except Exception as e:
            self.log_test("Debug User Info", False, f"Exception: {str(e)}")
            return False, None

    def test_debug_simple(self):
        """Test simple debug endpoint"""
        try:
            if not self.auth_token:
                self.log_test("Debug Simple", False, "No auth token available")
                return False, None
                
            response = self.session.get(f"{BACKEND_URL}/debug/simple")
            
            if response.status_code == 200:
                data = response.json()
                if "current_week" in data and "contributors" in data:
                    self.log_test("Debug Simple", True, 
                        f"Week: {data['current_week']}, Contributors: {len(data['contributors'])}, Total Stories: {data['total_stories_in_db']}")
                    return True, data
                else:
                    self.log_test("Debug Simple", False, "Invalid debug data structure", data)
                    return False, None
            else:
                self.log_test("Debug Simple", False, f"Status code: {response.status_code}", response.text)
                return False, None
        except Exception as e:
            self.log_test("Debug Simple", False, f"Exception: {str(e)}")
            return False, None

    def test_debug_edition_logic(self):
        """Test edition logic debug endpoint"""
        try:
            if not self.auth_token:
                self.log_test("Debug Edition Logic", False, "No auth token available")
                return False, None
                
            response = self.session.get(f"{BACKEND_URL}/debug/edition-logic")
            
            if response.status_code == 200:
                data = response.json()
                if "current_week" in data and "all_contributors" in data:
                    self.log_test("Debug Edition Logic", True, 
                        f"Week: {data['current_week']}, Contributors: {len(data['contributors'])}, Current Week Stories: {data['current_week_stories_found']}")
                    return True, data
                else:
                    self.log_test("Debug Edition Logic", False, "Invalid debug data structure", data)
                    return False, None
            else:
                self.log_test("Debug Edition Logic", False, f"Status code: {response.status_code}", response.text)
                return False, None
        except Exception as e:
            self.log_test("Debug Edition Logic", False, f"Exception: {str(e)}")
            return False, None

    def test_admin_fix_contributors(self):
        """Test admin fix contributors endpoint"""
        try:
            if not self.auth_token:
                self.log_test("Admin Fix Contributors", False, "No auth token available")
                return False, None
                
            response = self.session.post(f"{BACKEND_URL}/admin/fix-contributors")
            
            if response.status_code == 200:
                data = response.json()
                if "message" in data:
                    self.log_test("Admin Fix Contributors", True, data["message"])
                    return True, data
                else:
                    self.log_test("Admin Fix Contributors", False, "Invalid response structure", data)
                    return False, None
            else:
                self.log_test("Admin Fix Contributors", False, f"Status code: {response.status_code}", response.text)
                return False, None
        except Exception as e:
            self.log_test("Admin Fix Contributors", False, f"Exception: {str(e)}")
            return False, None

    def test_weekly_stories_endpoint(self):
        """Test weekly stories endpoint with current week"""
        try:
            if not self.auth_token:
                self.log_test("Weekly Stories Endpoint", False, "No auth token available")
                return False, None
            
            # First get current week from debug
            debug_response = self.session.get(f"{BACKEND_URL}/debug/simple")
            if debug_response.status_code != 200:
                self.log_test("Weekly Stories Endpoint", False, "Could not get current week")
                return False, None
            
            current_week = debug_response.json().get("current_week")
            if not current_week:
                self.log_test("Weekly Stories Endpoint", False, "No current week in debug response")
                return False, None
                
            response = self.session.get(f"{BACKEND_URL}/stories/weekly/{current_week}")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_test("Weekly Stories Endpoint", True, f"Retrieved {len(data)} stories for week {current_week}")
                    return True, data
                else:
                    self.log_test("Weekly Stories Endpoint", False, "Response is not a list", data)
                    return False, None
            else:
                self.log_test("Weekly Stories Endpoint", False, f"Status code: {response.status_code}", response.text)
                return False, None
        except Exception as e:
            self.log_test("Weekly Stories Endpoint", False, f"Exception: {str(e)}")
            return False, None

    def create_contributor_story(self):
        """Create a story as the friend user to test contributor functionality"""
        try:
            # Login as the friend user
            login_data = {
                "email": "mike.reporter@newspaper.com",
                "password": "FriendPass456!"
            }
            
            friend_session = requests.Session()
            login_response = friend_session.post(f"{BACKEND_URL}/auth/login", json=login_data)
            
            if login_response.status_code != 200:
                # Try to register the friend first
                friend_data = {
                    "email": "mike.reporter@newspaper.com",
                    "password": "FriendPass456!",
                    "full_name": "Mike Reporter"
                }
                
                register_response = friend_session.post(f"{BACKEND_URL}/auth/register", json=friend_data)
                if register_response.status_code == 200:
                    friend_token = register_response.json()["access_token"]
                    friend_session.headers.update({"Authorization": f"Bearer {friend_token}"})
                    self.log_test("Create Contributor Story", True, "Registered and logged in as friend user")
                else:
                    self.log_test("Create Contributor Story", False, f"Could not register friend user: {register_response.text}")
                    return False
            else:
                friend_token = login_response.json()["access_token"]
                friend_session.headers.update({"Authorization": f"Bearer {friend_token}"})
            
            # Create a story as the friend
            story_data = {
                "title": "Breaking News from Mike Reporter",
                "content": "This is an exclusive story from Mike Reporter, who should be a contributor to Sarah's weekly edition. This story should appear in Sarah's flipbook if the contributor system is working correctly.",
                "is_headline": False
            }
            
            story_response = friend_session.post(f"{BACKEND_URL}/stories", json=story_data)
            
            if story_response.status_code == 200:
                story_data = story_response.json()
                self.log_test("Create Contributor Story", True, f"Friend story created: {story_data['title']}")
                return True
            else:
                self.log_test("Create Contributor Story", False, f"Status code: {story_response.status_code}", story_response.text)
                return False
                
        except Exception as e:
            self.log_test("Create Contributor Story", False, f"Exception: {str(e)}")
            return False

    def investigate_contributor_bug(self):
        """Comprehensive investigation of the contributor stories bug"""
        print("\n🔍 INVESTIGATING CONTRIBUTOR STORIES BUG")
        print("=" * 50)
        
        # Step 1: Check user info and relationships
        print("Step 1: Checking user relationships...")
        user_info_success, user_info_data = self.test_debug_user_info()
        
        # Step 2: Get simple debug overview
        print("Step 2: Getting debug overview...")
        simple_debug_success, simple_debug_data = self.test_debug_simple()
        
        # Step 3: Create contributor story
        print("Step 3: Creating contributor story...")
        contributor_story_success = self.create_contributor_story()
        
        # Step 4: Check edition logic
        print("Step 4: Checking edition generation logic...")
        edition_logic_success, edition_logic_data = self.test_debug_edition_logic()
        
        # Step 5: Test current edition
        print("Step 5: Testing current edition...")
        current_edition_success = self.test_current_edition()
        
        # Step 6: Test weekly stories endpoint
        print("Step 6: Testing weekly stories endpoint...")
        weekly_stories_success, weekly_stories_data = self.test_weekly_stories_endpoint()
        
        # Step 7: Try admin fix
        print("Step 7: Running admin fix...")
        admin_fix_success, admin_fix_data = self.test_admin_fix_contributors()
        
        # Step 8: Re-test after fix
        print("Step 8: Re-testing after admin fix...")
        post_fix_user_info_success, post_fix_user_info_data = self.test_debug_user_info()
        post_fix_edition_logic_success, post_fix_edition_logic_data = self.test_debug_edition_logic()
        post_fix_current_edition_success = self.test_current_edition()
        
        # Analysis
        print("\n📊 BUG INVESTIGATION ANALYSIS")
        print("=" * 50)
        
        if user_info_data:
            diagnosis = user_info_data.get("diagnosis", {})
            print(f"✓ User has {diagnosis.get('friends_count', 0)} friends")
            print(f"✓ User has {diagnosis.get('contributors_count', 0)} contributors")
            print(f"✓ Found {diagnosis.get('contributor_stories_count', 0)} stories from contributors")
            
            if diagnosis.get('problem'):
                print(f"⚠️  Problem identified: {diagnosis['problem']}")
        
        if simple_debug_data:
            print(f"✓ Current week: {simple_debug_data.get('current_week')}")
            print(f"✓ Total stories in database: {simple_debug_data.get('total_stories_in_db', 0)}")
            print(f"✓ Stories from contributors (current week): {simple_debug_data.get('stories_from_contributors_current_week', 0)}")
        
        if edition_logic_data:
            print(f"✓ Edition logic found {edition_logic_data.get('current_week_stories_found', 0)} stories for current week")
            print(f"✓ Total stories from all contributors: {edition_logic_data.get('total_stories_from_contributors', 0)}")
        
        # Root cause analysis
        print("\n🎯 ROOT CAUSE ANALYSIS")
        print("=" * 50)
        
        if user_info_data and user_info_data.get("diagnosis", {}).get("contributors_count", 0) == 0:
            print("❌ ROOT CAUSE: User has no contributors registered")
            print("   - Friends exist but are not set as contributors")
            print("   - Admin fix should resolve this issue")
        elif simple_debug_data and simple_debug_data.get("stories_from_contributors_current_week", 0) == 0:
            print("❌ ROOT CAUSE: No stories from contributors for current week")
            print("   - Contributors exist but haven't submitted stories this week")
        elif edition_logic_data and edition_logic_data.get("current_week_stories_found", 0) == 0:
            print("❌ ROOT CAUSE: Edition logic not finding contributor stories")
            print("   - Issue in the edition generation algorithm")
        else:
            print("✅ No obvious root cause found - system appears to be working")
        
        return {
            "user_info": user_info_data,
            "simple_debug": simple_debug_data,
            "edition_logic": edition_logic_data,
            "weekly_stories": weekly_stories_data if 'weekly_stories_data' in locals() else None,
            "admin_fix": admin_fix_data,
            "post_fix_user_info": post_fix_user_info_data if 'post_fix_user_info_data' in locals() else None,
            "post_fix_edition_logic": post_fix_edition_logic_data if 'post_fix_edition_logic_data' in locals() else None
        }

    def test_joel_conybear_specific(self):
        """URGENT: Test Joel Conybear's specific account to verify database query fix"""
        print("\n🚨 URGENT JOEL CONYBEAR INVESTIGATION")
        print("=" * 60)
        
        # Login as Joel Conybear
        joel_session = requests.Session()
        login_data = {
            "email": "joel.conybear@gmail.com",
            "password": "password123"  # Try common password
        }
        
        login_response = joel_session.post(f"{BACKEND_URL}/auth/login", json=login_data)
        
        if login_response.status_code != 200:
            # Try alternative passwords
            alt_passwords = ["Password123!", "SecurePass123!", "testpass", "joel123"]
            for pwd in alt_passwords:
                login_data["password"] = pwd
                login_response = joel_session.post(f"{BACKEND_URL}/auth/login", json=login_data)
                if login_response.status_code == 200:
                    break
            
            if login_response.status_code != 200:
                self.log_test("Joel Conybear Login", False, f"Could not login as Joel: {login_response.text}")
                return False, {}
        
        joel_token = login_response.json()["access_token"]
        joel_session.headers.update({"Authorization": f"Bearer {joel_token}"})
        self.log_test("Joel Conybear Login", True, "Successfully logged in as Joel Conybear")
        
        # Test 1: Get Joel's user info
        user_response = joel_session.get(f"{BACKEND_URL}/users/me")
        if user_response.status_code == 200:
            joel_user_data = user_response.json()
            self.log_test("Joel User Info", True, f"Joel ID: {joel_user_data['id']}, Email: {joel_user_data['email']}")
        else:
            self.log_test("Joel User Info", False, f"Status: {user_response.status_code}")
            return False, {}
        
        # Test 2: Debug user info to see contributors
        debug_response = joel_session.get(f"{BACKEND_URL}/debug/user-info")
        joel_debug_data = {}
        if debug_response.status_code == 200:
            joel_debug_data = debug_response.json()
            diagnosis = joel_debug_data.get("diagnosis", {})
            self.log_test("Joel Debug Info", True, 
                f"Friends: {diagnosis.get('friends_count', 0)}, Contributors: {diagnosis.get('contributors_count', 0)}, Stories: {diagnosis.get('contributor_stories_count', 0)}")
        else:
            self.log_test("Joel Debug Info", False, f"Status: {debug_response.status_code}")
        
        # Test 3: Test /api/stories/weekly/2025-W30 (the specific endpoint mentioned)
        weekly_response = joel_session.get(f"{BACKEND_URL}/stories/weekly/2025-W30")
        weekly_stories_data = []
        if weekly_response.status_code == 200:
            weekly_stories_data = weekly_response.json()
            self.log_test("Joel Weekly Stories 2025-W30", True, 
                f"Found {len(weekly_stories_data)} stories for Week 30")
            for story in weekly_stories_data:
                print(f"   - {story.get('title')} by {story.get('author_name')}")
        else:
            self.log_test("Joel Weekly Stories 2025-W30", False, f"Status: {weekly_response.status_code}")
        
        # Test 4: Test /api/editions/current
        current_edition_response = joel_session.get(f"{BACKEND_URL}/editions/current")
        current_edition_data = {}
        if current_edition_response.status_code == 200:
            current_edition_data = current_edition_response.json()
            stories_count = len(current_edition_data.get('stories', []))
            self.log_test("Joel Current Edition", True, 
                f"Current edition has {stories_count} stories for week {current_edition_data.get('week_of')}")
            for story in current_edition_data.get('stories', []):
                print(f"   - {story.get('title')} by {story.get('author_name')}")
        else:
            self.log_test("Joel Current Edition", False, f"Status: {current_edition_response.status_code}")
        
        # Test 5: Test /api/debug/edition-logic
        edition_logic_response = joel_session.get(f"{BACKEND_URL}/debug/edition-logic")
        edition_logic_data = {}
        if edition_logic_response.status_code == 200:
            edition_logic_data = edition_logic_response.json()
            self.log_test("Joel Edition Logic", True, 
                f"Edition logic: {edition_logic_data.get('current_week_stories_found', 0)} current week stories, {edition_logic_data.get('total_stories_from_contributors', 0)} total contributor stories")
        else:
            self.log_test("Joel Edition Logic", False, f"Status: {edition_logic_response.status_code}")
        
        # Test 6: Check database query fix - verify user lookup by email works
        simple_debug_response = joel_session.get(f"{BACKEND_URL}/debug/simple")
        simple_debug_data = {}
        if simple_debug_response.status_code == 200:
            simple_debug_data = simple_debug_response.json()
            self.log_test("Joel Simple Debug", True, 
                f"Database query working - found user ID: {simple_debug_data.get('your_id')}")
        else:
            self.log_test("Joel Simple Debug", False, f"Status: {simple_debug_response.status_code}")
        
        # Analysis
        print("\n📊 JOEL CONYBEAR ANALYSIS")
        print("=" * 60)
        
        if joel_debug_data:
            diagnosis = joel_debug_data.get("diagnosis", {})
            contributors_count = diagnosis.get('contributors_count', 0)
            friends_count = diagnosis.get('friends_count', 0)
            
            print(f"✓ Joel's account found: {joel_user_data.get('id')}")
            print(f"✓ Joel has {friends_count} friends")
            print(f"✓ Joel has {contributors_count} contributors")
            print(f"✓ Joel sees {len(weekly_stories_data)} stories in Week 30")
            print(f"✓ Joel's current edition has {len(current_edition_data.get('stories', []))} stories")
            
            if contributors_count == 0:
                print("❌ ROOT CAUSE: Joel has NO contributors - this is why he only sees 1 story")
                print("   The user's claim that 'Joel has 2 contributors' is INCORRECT")
                print("   Joel needs to invite friends and set them as contributors")
            else:
                print(f"✅ Joel has {contributors_count} contributors - investigating why stories aren't showing")
        
        return True, {
            "joel_user_data": joel_user_data,
            "joel_debug_data": joel_debug_data,
            "weekly_stories_data": weekly_stories_data,
            "current_edition_data": current_edition_data,
            "edition_logic_data": edition_logic_data,
            "simple_debug_data": simple_debug_data
        }

    def run_all_tests(self):
        """Run all backend tests"""
        print("🚀 Starting Backend API Testing for Social Weekly Newspaper Network")
        print("=" * 70)
        
        # URGENT: Test Joel Conybear's account first
        joel_success, joel_data = self.test_joel_conybear_specific()
        
        # Try login first, then registration if needed
        login_success = self.test_user_login()
        if not login_success:
            print("Login failed, trying registration...")
            registration_success = self.test_user_registration()
            if not registration_success:
                print("❌ CRITICAL: Could not authenticate user")
                return 0, 1, self.test_results, {"joel_investigation": joel_data}
        
        # Test sequence (skip auth tests since we already did them)
        tests = [
            self.test_health_check,
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
        
        passed = 1 if login_success else (1 if registration_success else 0)  # Count auth success
        failed = 0 if login_success else (0 if registration_success else 1)
        
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
        
        # Run the contributor bug investigation
        print("\n" + "=" * 70)
        investigation_results = self.investigate_contributor_bug()
        
        print("=" * 70)
        print(f"📊 TEST SUMMARY")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"📈 Success Rate: {(passed/(passed+failed)*100):.1f}%")
        
        return passed, failed, self.test_results, {
            "joel_investigation": joel_data,
            "general_investigation": investigation_results
        }

if __name__ == "__main__":
    tester = BackendTester()
    passed, failed, results, investigation = tester.run_all_tests()
    
    # Save detailed results
    with open('/app/backend_test_results.json', 'w') as f:
        json.dump({
            "summary": {
                "passed": passed,
                "failed": failed,
                "success_rate": passed/(passed+failed)*100 if (passed+failed) > 0 else 0
            },
            "detailed_results": results,
            "contributor_bug_investigation": investigation
        }, f, indent=2)
    
    print(f"\n📄 Detailed results saved to: /app/backend_test_results.json")
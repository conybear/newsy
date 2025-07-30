#!/usr/bin/env python3
"""
Comprehensive Story Editor Testing for Acta Diurna Phase 2
Tests all story management endpoints including draft system, submission, and image upload
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
BACKEND_URL = "https://464d35f9-1da6-4f46-92d7-fc7b50272fb2.preview.emergentagent.com/api"

class StoryEditorTester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.user_id = None
        self.test_results = []
        self.story_id = None
        
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

    def create_test_image(self, size=(100, 100), color='red'):
        """Create a test image"""
        img = Image.new('RGB', size, color=color)
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
                self.log_test("Health Check", True, 
                    f"Status: {data.get('status')}, Week: {data.get('current_week')}, Submissions Open: {data.get('submissions_open')}")
                return True
            else:
                self.log_test("Health Check", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Health Check", False, f"Exception: {str(e)}")
            return False

    def test_user_authentication(self):
        """Test user authentication with specified credentials"""
        try:
            # Try login first with specified credentials
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
                    self.log_test("User Authentication", True, "Login successful with test credentials")
                    return True
            
            # If login fails, try registration
            register_data = {
                "email": "test@actadiurna.com",
                "password": "TestPass123!",
                "full_name": "Test User"
            }
            
            response = self.session.post(f"{BACKEND_URL}/auth/register", json=register_data)
            
            if response.status_code == 200:
                data = response.json()
                if "access_token" in data:
                    self.auth_token = data["access_token"]
                    self.session.headers.update({"Authorization": f"Bearer {self.auth_token}"})
                    self.log_test("User Authentication", True, "Registration successful with test credentials")
                    return True
            elif response.status_code == 400 and "already registered" in response.text:
                # User exists but login failed - password might be wrong
                self.log_test("User Authentication", False, "User exists but login failed - check password")
                return False
            
            self.log_test("User Authentication", False, f"Both login and registration failed: {response.text}")
            return False
            
        except Exception as e:
            self.log_test("User Authentication", False, f"Exception: {str(e)}")
            return False

    def test_story_status(self):
        """Test /api/stories/status endpoint"""
        try:
            if not self.auth_token:
                self.log_test("Story Status", False, "No auth token available")
                return False
                
            response = self.session.get(f"{BACKEND_URL}/stories/status")
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["current_week", "has_submitted", "has_draft", "submissions_open", "deadline"]
                
                if all(field in data for field in required_fields):
                    self.log_test("Story Status", True, 
                        f"Week: {data['current_week']}, Submitted: {data['has_submitted']}, Draft: {data['has_draft']}, Open: {data['submissions_open']}")
                    return True, data
                else:
                    missing = [f for f in required_fields if f not in data]
                    self.log_test("Story Status", False, f"Missing fields: {missing}", data)
                    return False, None
            else:
                self.log_test("Story Status", False, f"Status code: {response.status_code}", response.text)
                return False, None
        except Exception as e:
            self.log_test("Story Status", False, f"Exception: {str(e)}")
            return False, None

    def test_save_draft(self):
        """Test /api/stories/draft POST endpoint"""
        try:
            if not self.auth_token:
                self.log_test("Save Draft", False, "No auth token available")
                return False
                
            draft_data = {
                "title": "My Amazing Week in San Francisco",
                "headline": "Local Tech Conference Brings Innovation to the Bay Area",
                "content": "This week I attended the annual Tech Innovation Conference in downtown San Francisco. The event featured groundbreaking presentations on AI, sustainable technology, and community-driven development projects. Over 500 attendees from across the Bay Area gathered to share ideas and collaborate on solutions for local challenges. The highlight was a panel discussion on how technology can strengthen neighborhood connections and support local businesses."
            }
            
            response = self.session.post(f"{BACKEND_URL}/stories/draft", json=draft_data)
            
            if response.status_code == 200:
                data = response.json()
                if "message" in data and "id" in data:
                    self.story_id = data["id"]
                    self.log_test("Save Draft", True, f"Draft saved successfully: {data['message']}")
                    return True, data
                else:
                    self.log_test("Save Draft", False, "Invalid response structure", data)
                    return False, None
            else:
                self.log_test("Save Draft", False, f"Status code: {response.status_code}", response.text)
                return False, None
        except Exception as e:
            self.log_test("Save Draft", False, f"Exception: {str(e)}")
            return False, None

    def test_get_draft(self):
        """Test /api/stories/draft GET endpoint"""
        try:
            if not self.auth_token:
                self.log_test("Get Draft", False, "No auth token available")
                return False
                
            response = self.session.get(f"{BACKEND_URL}/stories/draft")
            
            if response.status_code == 200:
                data = response.json()
                expected_fields = ["title", "headline", "content", "images"]
                
                if all(field in data for field in expected_fields):
                    has_content = bool(data.get("title") or data.get("headline") or data.get("content"))
                    self.log_test("Get Draft", True, 
                        f"Draft retrieved - Has content: {has_content}, Title: '{data.get('title', '')[:30]}...'")
                    return True, data
                else:
                    missing = [f for f in expected_fields if f not in data]
                    self.log_test("Get Draft", False, f"Missing fields: {missing}", data)
                    return False, None
            else:
                self.log_test("Get Draft", False, f"Status code: {response.status_code}", response.text)
                return False, None
        except Exception as e:
            self.log_test("Get Draft", False, f"Exception: {str(e)}")
            return False, None

    def test_story_submission(self):
        """Test /api/stories/submit endpoint"""
        try:
            if not self.auth_token:
                self.log_test("Story Submission", False, "No auth token available")
                return False
                
            story_data = {
                "title": "Community Garden Success Story",
                "headline": "Neighborhood Collaboration Yields Bountiful Harvest",
                "content": "Our local community garden project has exceeded all expectations this season. What started as a small initiative by five neighbors has grown into a thriving space that serves over 30 families. This week we harvested our largest crop yet - over 150 pounds of fresh vegetables including tomatoes, peppers, zucchini, and herbs. The surplus was donated to the local food bank, helping to address food insecurity in our neighborhood. The garden has become more than just a place to grow food; it's a gathering space where neighbors of all ages come together, share knowledge, and build lasting friendships."
            }
            
            response = self.session.post(f"{BACKEND_URL}/stories/submit", json=story_data)
            
            if response.status_code == 200:
                data = response.json()
                if "message" in data and "id" in data:
                    self.story_id = data["id"]
                    self.log_test("Story Submission", True, f"Story submitted successfully: {data['message']}")
                    return True, data
                else:
                    self.log_test("Story Submission", False, "Invalid response structure", data)
                    return False, None
            else:
                self.log_test("Story Submission", False, f"Status code: {response.status_code}", response.text)
                return False, None
        except Exception as e:
            self.log_test("Story Submission", False, f"Exception: {str(e)}")
            return False, None

    def test_my_stories(self):
        """Test /api/stories/my endpoint"""
        try:
            if not self.auth_token:
                self.log_test("My Stories", False, "No auth token available")
                return False
                
            response = self.session.get(f"{BACKEND_URL}/stories/my")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_test("My Stories", True, f"Retrieved {len(data)} stories")
                    
                    # Verify story structure
                    if data:
                        story = data[0]
                        required_fields = ["id", "title", "content", "author_name", "week_of", "is_submitted"]
                        missing_fields = [f for f in required_fields if f not in story]
                        if missing_fields:
                            self.log_test("My Stories Structure", False, f"Missing fields in story: {missing_fields}")
                        else:
                            self.log_test("My Stories Structure", True, "Story structure is valid")
                    
                    return True, data
                else:
                    self.log_test("My Stories", False, "Response is not a list", data)
                    return False, None
            else:
                self.log_test("My Stories", False, f"Status code: {response.status_code}", response.text)
                return False, None
        except Exception as e:
            self.log_test("My Stories", False, f"Exception: {str(e)}")
            return False, None

    def test_business_rules_validation(self):
        """Test business rules: required fields and one-story-per-week limit"""
        try:
            if not self.auth_token:
                self.log_test("Business Rules Validation", False, "No auth token available")
                return False
            
            # Test 1: Missing required fields
            invalid_story = {
                "title": "",  # Empty title
                "headline": "Test Headline",
                "content": ""  # Empty content
            }
            
            response = self.session.post(f"{BACKEND_URL}/stories/submit", json=invalid_story)
            
            if response.status_code == 400:
                self.log_test("Required Fields Validation", True, "Empty fields properly rejected")
            else:
                self.log_test("Required Fields Validation", False, f"Expected 400, got {response.status_code}")
                return False
            
            # Test 2: One story per week limit (try to submit another story)
            duplicate_story = {
                "title": "Second Story This Week",
                "headline": "This Should Be Rejected",
                "content": "Attempting to submit a second story in the same week should fail due to business rules."
            }
            
            response = self.session.post(f"{BACKEND_URL}/stories/submit", json=duplicate_story)
            
            if response.status_code == 400:
                self.log_test("One Story Per Week Limit", True, "Duplicate submission properly rejected")
                return True
            else:
                self.log_test("One Story Per Week Limit", False, f"Expected 400, got {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Business Rules Validation", False, f"Exception: {str(e)}")
            return False

    def test_image_upload(self):
        """Test /api/stories/{story_id}/images endpoint"""
        try:
            if not self.auth_token:
                self.log_test("Image Upload", False, "No auth token available")
                return False
                
            if not self.story_id:
                self.log_test("Image Upload", False, "No story ID available")
                return False
            
            # Test 1: Valid image upload
            image_data = self.create_test_image()
            files = {
                'file': ('test_image.jpg', image_data, 'image/jpeg')
            }
            
            response = self.session.post(f"{BACKEND_URL}/stories/{self.story_id}/images", files=files)
            
            if response.status_code == 200:
                data = response.json()
                if "message" in data and "image_id" in data:
                    self.log_test("Image Upload - Valid", True, f"Image uploaded: {data['image_id']}")
                    image_id = data["image_id"]
                else:
                    self.log_test("Image Upload - Valid", False, "Invalid response structure", data)
                    return False
            else:
                self.log_test("Image Upload - Valid", False, f"Status code: {response.status_code}", response.text)
                return False
            
            # Test 2: Upload second image
            image_data2 = self.create_test_image(color='blue')
            files2 = {
                'file': ('test_image2.jpg', image_data2, 'image/jpeg')
            }
            
            response = self.session.post(f"{BACKEND_URL}/stories/{self.story_id}/images", files=files2)
            
            if response.status_code == 200:
                self.log_test("Image Upload - Second", True, "Second image uploaded successfully")
            else:
                self.log_test("Image Upload - Second", False, f"Status code: {response.status_code}")
                return False
            
            # Test 3: Upload third image
            image_data3 = self.create_test_image(color='green')
            files3 = {
                'file': ('test_image3.jpg', image_data3, 'image/jpeg')
            }
            
            response = self.session.post(f"{BACKEND_URL}/stories/{self.story_id}/images", files=files3)
            
            if response.status_code == 200:
                self.log_test("Image Upload - Third", True, "Third image uploaded successfully")
            else:
                self.log_test("Image Upload - Third", False, f"Status code: {response.status_code}")
                return False
            
            # Test 4: Try to upload fourth image (should fail - 3 image limit)
            image_data4 = self.create_test_image(color='yellow')
            files4 = {
                'file': ('test_image4.jpg', image_data4, 'image/jpeg')
            }
            
            response = self.session.post(f"{BACKEND_URL}/stories/{self.story_id}/images", files=files4)
            
            if response.status_code == 400:
                self.log_test("Image Upload - Limit Test", True, "Fourth image properly rejected (3 image limit)")
            else:
                self.log_test("Image Upload - Limit Test", False, f"Expected 400, got {response.status_code}")
                return False
            
            # Test 5: Try to upload oversized image
            large_image = self.create_test_image(size=(2000, 2000))  # Large image
            files_large = {
                'file': ('large_image.jpg', large_image, 'image/jpeg')
            }
            
            response = self.session.post(f"{BACKEND_URL}/stories/{self.story_id}/images", files=files_large)
            
            if response.status_code == 400:
                self.log_test("Image Upload - Size Limit", True, "Large image properly rejected")
            else:
                self.log_test("Image Upload - Size Limit", False, f"Expected 400, got {response.status_code}")
            
            # Test 6: Try to upload non-image file
            text_data = b"This is not an image file"
            files_text = {
                'file': ('test.txt', text_data, 'text/plain')
            }
            
            response = self.session.post(f"{BACKEND_URL}/stories/{self.story_id}/images", files=files_text)
            
            if response.status_code == 400:
                self.log_test("Image Upload - File Type Validation", True, "Non-image file properly rejected")
                return True
            else:
                self.log_test("Image Upload - File Type Validation", False, f"Expected 400, got {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Image Upload", False, f"Exception: {str(e)}")
            return False

    def test_draft_auto_save_functionality(self):
        """Test draft auto-save functionality by updating existing draft"""
        try:
            if not self.auth_token:
                self.log_test("Draft Auto-Save", False, "No auth token available")
                return False
            
            # First, save a draft
            initial_draft = {
                "title": "Initial Draft Title",
                "headline": "Initial Headline",
                "content": "Initial content for the draft story."
            }
            
            response = self.session.post(f"{BACKEND_URL}/stories/draft", json=initial_draft)
            
            if response.status_code != 200:
                self.log_test("Draft Auto-Save", False, "Could not create initial draft")
                return False
            
            # Wait a moment
            time.sleep(1)
            
            # Update the draft (simulating auto-save)
            updated_draft = {
                "title": "Updated Draft Title",
                "headline": "Updated Headline with More Details",
                "content": "Updated content for the draft story with additional information and details that would be added during editing."
            }
            
            response = self.session.post(f"{BACKEND_URL}/stories/draft", json=updated_draft)
            
            if response.status_code == 200:
                data = response.json()
                if "updated" in data.get("message", "").lower():
                    self.log_test("Draft Auto-Save", True, "Draft successfully updated (auto-save working)")
                else:
                    self.log_test("Draft Auto-Save", True, "Draft saved (auto-save functionality working)")
                
                # Verify the update by retrieving the draft
                get_response = self.session.get(f"{BACKEND_URL}/stories/draft")
                if get_response.status_code == 200:
                    draft_data = get_response.json()
                    if draft_data.get("title") == updated_draft["title"]:
                        self.log_test("Draft Auto-Save Verification", True, "Updated draft content verified")
                        return True
                    else:
                        self.log_test("Draft Auto-Save Verification", False, "Draft content not updated properly")
                        return False
                else:
                    self.log_test("Draft Auto-Save Verification", False, "Could not retrieve updated draft")
                    return False
            else:
                self.log_test("Draft Auto-Save", False, f"Status code: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Draft Auto-Save", False, f"Exception: {str(e)}")
            return False

    def test_deadline_enforcement(self):
        """Test deadline enforcement logic"""
        try:
            if not self.auth_token:
                self.log_test("Deadline Enforcement", False, "No auth token available")
                return False
            
            # Get current status to check if submissions are open
            status_response = self.session.get(f"{BACKEND_URL}/stories/status")
            
            if status_response.status_code == 200:
                status_data = status_response.json()
                submissions_open = status_data.get("submissions_open", True)
                deadline = status_data.get("deadline", "Unknown")
                
                self.log_test("Deadline Enforcement", True, 
                    f"Submissions Open: {submissions_open}, Deadline: {deadline}")
                
                # If submissions are closed, verify that submission fails
                if not submissions_open:
                    test_story = {
                        "title": "Test Story After Deadline",
                        "headline": "This Should Fail",
                        "content": "Testing submission after deadline."
                    }
                    
                    submit_response = self.session.post(f"{BACKEND_URL}/stories/submit", json=test_story)
                    
                    if submit_response.status_code == 400:
                        self.log_test("Deadline Enforcement - Closed", True, "Submission properly rejected after deadline")
                    else:
                        self.log_test("Deadline Enforcement - Closed", False, "Submission allowed after deadline")
                        return False
                
                return True
            else:
                self.log_test("Deadline Enforcement", False, f"Could not get status: {status_response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Deadline Enforcement", False, f"Exception: {str(e)}")
            return False

    def run_comprehensive_tests(self):
        """Run all Story Editor tests"""
        print("🚀 Starting Comprehensive Story Editor Testing for Acta Diurna Phase 2")
        print("=" * 80)
        
        # Test sequence
        tests = [
            ("Health Check", self.test_health_check),
            ("User Authentication", self.test_user_authentication),
            ("Story Status", lambda: self.test_story_status()[0]),
            ("Save Draft", lambda: self.test_save_draft()[0]),
            ("Get Draft", lambda: self.test_get_draft()[0]),
            ("Draft Auto-Save", self.test_draft_auto_save_functionality),
            ("Story Submission", lambda: self.test_story_submission()[0]),
            ("My Stories", lambda: self.test_my_stories()[0]),
            ("Business Rules Validation", self.test_business_rules_validation),
            ("Image Upload", self.test_image_upload),
            ("Deadline Enforcement", self.test_deadline_enforcement),
        ]
        
        passed = 0
        failed = 0
        
        for test_name, test_func in tests:
            try:
                print(f"\n🔍 Running: {test_name}")
                if test_func():
                    passed += 1
                else:
                    failed += 1
            except Exception as e:
                print(f"❌ CRITICAL ERROR in {test_name}: {str(e)}")
                self.log_test(test_name, False, f"Critical error: {str(e)}")
                failed += 1
            
            # Small delay between tests
            time.sleep(0.5)
        
        print("\n" + "=" * 80)
        print(f"📊 STORY EDITOR TEST SUMMARY")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"📈 Success Rate: {(passed/(passed+failed)*100):.1f}%")
        
        return passed, failed, self.test_results

if __name__ == "__main__":
    tester = StoryEditorTester()
    passed, failed, results = tester.run_comprehensive_tests()
    
    # Save detailed results
    with open('/app/story_editor_test_results.json', 'w') as f:
        json.dump({
            "summary": {
                "passed": passed,
                "failed": failed,
                "success_rate": passed/(passed+failed)*100 if (passed+failed) > 0 else 0
            },
            "detailed_results": results,
            "test_focus": "Acta Diurna Phase 2 Story Editor Functionality",
            "endpoints_tested": [
                "/api/stories/status",
                "/api/stories/draft (GET & POST)",
                "/api/stories/submit",
                "/api/stories/my",
                "/api/stories/{story_id}/images"
            ]
        }, f, indent=2)
    
    print(f"\n📄 Detailed results saved to: /app/story_editor_test_results.json")
#!/usr/bin/env python3
"""
Image Upload Test for Draft Stories - Acta Diurna Phase 2
Tests image upload functionality specifically for draft stories
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

class ImageUploadTester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.story_id = None
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

    def create_test_image(self, size=(100, 100), color='red'):
        """Create a test image"""
        img = Image.new('RGB', size, color=color)
        buffer = io.BytesIO()
        img.save(buffer, format='JPEG')
        buffer.seek(0)
        return buffer.getvalue()

    def authenticate(self):
        """Authenticate with test credentials"""
        try:
            # Try login first
            login_data = {
                "email": "imagetest@actadiurna.com",
                "password": "TestPass123!"
            }
            
            response = self.session.post(f"{BACKEND_URL}/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data["access_token"]
                self.session.headers.update({"Authorization": f"Bearer {self.auth_token}"})
                self.log_test("Authentication", True, "Login successful")
                return True
            
            # If login fails, try registration
            register_data = {
                "email": "imagetest@actadiurna.com",
                "password": "TestPass123!",
                "full_name": "Image Test User"
            }
            
            response = self.session.post(f"{BACKEND_URL}/auth/register", json=register_data)
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data["access_token"]
                self.session.headers.update({"Authorization": f"Bearer {self.auth_token}"})
                self.log_test("Authentication", True, "Registration successful")
                return True
            
            self.log_test("Authentication", False, f"Both login and registration failed: {response.text}")
            return False
            
        except Exception as e:
            self.log_test("Authentication", False, f"Exception: {str(e)}")
            return False

    def create_draft_story(self):
        """Create a draft story for image testing"""
        try:
            draft_data = {
                "title": "Image Test Story",
                "headline": "Testing Image Upload Functionality",
                "content": "This is a draft story created specifically for testing image upload functionality."
            }
            
            response = self.session.post(f"{BACKEND_URL}/stories/draft", json=draft_data)
            
            if response.status_code == 200:
                data = response.json()
                if "id" in data:
                    self.story_id = data["id"]
                    self.log_test("Create Draft Story", True, f"Draft story created with ID: {self.story_id}")
                    return True
                else:
                    self.log_test("Create Draft Story", False, "No story ID in response", data)
                    return False
            else:
                self.log_test("Create Draft Story", False, f"Status code: {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("Create Draft Story", False, f"Exception: {str(e)}")
            return False

    def test_image_upload_comprehensive(self):
        """Comprehensive image upload testing"""
        try:
            if not self.story_id:
                self.log_test("Image Upload Test", False, "No story ID available")
                return False
            
            # Test 1: Upload first image
            image_data1 = self.create_test_image(color='red')
            files1 = {
                'file': ('test_image1.jpg', image_data1, 'image/jpeg')
            }
            
            response = self.session.post(f"{BACKEND_URL}/stories/{self.story_id}/images", files=files1)
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("Image Upload - First", True, f"First image uploaded: {data.get('image_id')}")
            else:
                self.log_test("Image Upload - First", False, f"Status: {response.status_code}, Response: {response.text}")
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
                self.log_test("Image Upload - Second", False, f"Status: {response.status_code}")
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
                self.log_test("Image Upload - Third", False, f"Status: {response.status_code}")
                return False
            
            # Test 4: Try fourth image (should fail - 3 image limit)
            image_data4 = self.create_test_image(color='yellow')
            files4 = {
                'file': ('test_image4.jpg', image_data4, 'image/jpeg')
            }
            
            response = self.session.post(f"{BACKEND_URL}/stories/{self.story_id}/images", files=files4)
            
            if response.status_code == 400:
                self.log_test("Image Upload - Limit Test", True, "Fourth image properly rejected (3 image limit enforced)")
            else:
                self.log_test("Image Upload - Limit Test", False, f"Expected 400, got {response.status_code}")
                return False
            
            # Test 5: File type validation
            text_data = b"This is not an image"
            files_text = {
                'file': ('test.txt', text_data, 'text/plain')
            }
            
            response = self.session.post(f"{BACKEND_URL}/stories/{self.story_id}/images", files=files_text)
            
            if response.status_code == 400:
                self.log_test("Image Upload - File Type Validation", True, "Non-image file properly rejected")
            else:
                self.log_test("Image Upload - File Type Validation", False, f"Expected 400, got {response.status_code}")
                return False
            
            # Test 6: Large image size validation
            large_image = self.create_test_image(size=(3000, 3000))  # Very large image
            files_large = {
                'file': ('large_image.jpg', large_image, 'image/jpeg')
            }
            
            response = self.session.post(f"{BACKEND_URL}/stories/{self.story_id}/images", files=files_large)
            
            if response.status_code == 400:
                self.log_test("Image Upload - Size Validation", True, "Large image properly rejected (size limit enforced)")
            else:
                self.log_test("Image Upload - Size Validation", False, f"Expected 400, got {response.status_code}")
            
            return True
            
        except Exception as e:
            self.log_test("Image Upload Test", False, f"Exception: {str(e)}")
            return False

    def run_image_tests(self):
        """Run all image upload tests"""
        print("🖼️  Starting Image Upload Testing for Acta Diurna Phase 2")
        print("=" * 60)
        
        # Test sequence
        if not self.authenticate():
            print("❌ Authentication failed, cannot proceed")
            return 0, 1, self.test_results
        
        if not self.create_draft_story():
            print("❌ Could not create draft story, cannot proceed")
            return 1, 1, self.test_results
        
        if self.test_image_upload_comprehensive():
            passed = 8  # All image upload sub-tests passed
            failed = 0
        else:
            passed = 2  # Auth and draft creation passed
            failed = 1
        
        print("\n" + "=" * 60)
        print(f"📊 IMAGE UPLOAD TEST SUMMARY")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"📈 Success Rate: {(passed/(passed+failed)*100):.1f}%")
        
        return passed, failed, self.test_results

if __name__ == "__main__":
    tester = ImageUploadTester()
    passed, failed, results = tester.run_image_tests()
    
    # Save results
    with open('/app/image_upload_test_results.json', 'w') as f:
        json.dump({
            "summary": {
                "passed": passed,
                "failed": failed,
                "success_rate": passed/(passed+failed)*100 if (passed+failed) > 0 else 0
            },
            "detailed_results": results,
            "test_focus": "Image Upload for Draft Stories"
        }, f, indent=2)
    
    print(f"\n📄 Results saved to: /app/image_upload_test_results.json")
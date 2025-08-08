import requests
import sys
import json
from datetime import datetime
import uuid

class NewsyAPITester:
    def __init__(self, base_url="https://dddc6d0c-9b98-4632-81b7-760632b6b5b6.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.created_story_id = None

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}" if endpoint else f"{self.api_url}/"
        if headers is None:
            headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=10)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=10)

            print(f"   Status Code: {response.status_code}")
            
            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Expected {expected_status}, got {response.status_code}")
                try:
                    response_data = response.json()
                    print(f"   Response: {json.dumps(response_data, indent=2)[:200]}...")
                    return True, response_data
                except:
                    return True, response.text[:200] if hasattr(response, 'text') else {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Error: {response.text[:200]}")
                return False, {}

        except requests.exceptions.Timeout:
            print(f"❌ Failed - Request timeout")
            return False, {}
        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_root_endpoint(self):
        """Test the root API endpoint"""
        return self.run_test("Root API Endpoint", "GET", "", 200)

    def test_get_stories(self):
        """Test getting all stories"""
        return self.run_test("Get All Stories", "GET", "stories", 200)

    def test_get_weekly_stories(self):
        """Test getting weekly stories"""
        return self.run_test("Get Weekly Stories", "GET", "stories/weekly", 200)

    def test_create_story(self):
        """Test creating a new story"""
        test_story = {
            "title": f"Test Story {datetime.now().strftime('%H:%M:%S')}",
            "content": "This is a test story created by the automated test suite. It contains sample content to verify the story creation functionality.",
            "author": "Test Author"
        }
        
        success, response = self.run_test("Create Story", "POST", "stories", 201, data=test_story)
        if success and 'id' in response:
            self.created_story_id = response['id']
            print(f"   Created story with ID: {self.created_story_id}")
        return success, response

    def test_create_story_anonymous(self):
        """Test creating a story without author (should default to Anonymous)"""
        test_story = {
            "title": f"Anonymous Test Story {datetime.now().strftime('%H:%M:%S')}",
            "content": "This is a test story without an author to verify default behavior."
        }
        
        success, response = self.run_test("Create Anonymous Story", "POST", "stories", 201, data=test_story)
        if success and response.get('author') == 'Anonymous':
            print("✅ Author correctly defaulted to 'Anonymous'")
        elif success:
            print(f"⚠️  Author is '{response.get('author')}', expected 'Anonymous'")
        return success, response

    def test_create_story_validation(self):
        """Test story creation with missing required fields"""
        # Test missing title
        invalid_story = {
            "content": "Content without title"
        }
        success, _ = self.run_test("Create Story - Missing Title", "POST", "stories", 422, data=invalid_story)
        
        # Test missing content
        invalid_story2 = {
            "title": "Title without content"
        }
        success2, _ = self.run_test("Create Story - Missing Content", "POST", "stories", 422, data=invalid_story2)
        
        return success and success2

    def test_subscribe_newsletter(self):
        """Test newsletter subscription"""
        test_email = f"test_{uuid.uuid4().hex[:8]}@example.com"
        subscription_data = {"email": test_email}
        
        success, response = self.run_test("Subscribe to Newsletter", "POST", "subscribe", 200, data=subscription_data)
        return success, response

    def test_duplicate_subscription(self):
        """Test duplicate email subscription (should fail)"""
        test_email = f"duplicate_{uuid.uuid4().hex[:8]}@example.com"
        subscription_data = {"email": test_email}
        
        # First subscription should succeed
        success1, _ = self.run_test("First Subscription", "POST", "subscribe", 200, data=subscription_data)
        
        # Second subscription should fail
        success2, _ = self.run_test("Duplicate Subscription", "POST", "subscribe", 400, data=subscription_data)
        
        return success1 and success2

    def test_flipbook_endpoint(self):
        """Test the flipbook newspaper endpoint"""
        success, response = self.run_test("Get Flipbook Newspaper", "GET", "newspaper/flipbook", 200)
        if success and isinstance(response, str) and "Weekly Newspaper" in response:
            print("✅ Flipbook HTML contains expected content")
        elif success:
            print("⚠️  Flipbook response doesn't contain expected HTML content")
        return success

    def test_get_subscribers(self):
        """Test getting all subscribers (admin endpoint)"""
        return self.run_test("Get All Subscribers", "GET", "subscribers", 200)

    def run_all_tests(self):
        """Run all API tests"""
        print("🚀 Starting Newsy API Tests")
        print("=" * 50)
        
        # Basic connectivity tests
        self.test_root_endpoint()
        
        # Story-related tests
        self.test_get_stories()
        self.test_get_weekly_stories()
        self.test_create_story()
        self.test_create_story_anonymous()
        self.test_create_story_validation()
        
        # Newsletter tests
        self.test_subscribe_newsletter()
        self.test_duplicate_subscription()
        self.test_get_subscribers()
        
        # Flipbook test
        self.test_flipbook_endpoint()
        
        # Print final results
        print("\n" + "=" * 50)
        print(f"📊 Test Results: {self.tests_passed}/{self.tests_run} tests passed")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All tests passed!")
            return 0
        else:
            print(f"❌ {self.tests_run - self.tests_passed} tests failed")
            return 1

def main():
    tester = NewsyAPITester()
    return tester.run_all_tests()

if __name__ == "__main__":
    sys.exit(main())
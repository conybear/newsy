import requests
import sys
import json
from datetime import datetime
import uuid

class ActaDiurnaAPITester:
    def __init__(self, base_url="https://dddc6d0c-9b98-4632-81b7-760632b6b5b6.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.created_story_id = None
        self.created_draft_id = None

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
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=10)

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
        """Test the root API endpoint - should mention Acta Diurna"""
        success, response = self.run_test("Root API Endpoint", "GET", "", 200)
        if success and isinstance(response, dict) and "Personal Daily Chronicle" in response.get("message", ""):
            print("✅ Root endpoint contains Acta Diurna branding")
        elif success:
            print("⚠️  Root endpoint response doesn't contain expected Acta Diurna branding")
        return success, response

    def test_get_stories(self):
        """Test getting all stories from friends"""
        return self.run_test("Get All Stories from Friends", "GET", "stories", 200)

    def test_get_weekly_stories(self):
        """Test getting weekly stories from friends"""
        return self.run_test("Get Weekly Stories from Friends", "GET", "stories/weekly", 200)

    def test_create_story(self):
        """Test creating a new story to share with friends"""
        test_story = {
            "title": f"Friend Story {datetime.now().strftime('%H:%M:%S')}",
            "content": "This is a test story shared with my circle of friends. It contains sample content to verify the story creation functionality in Acta Diurna.",
            "author": "Test Friend"
        }
        
        success, response = self.run_test("Create Friend Story", "POST", "stories", 201, data=test_story)
        if success and 'id' in response:
            self.created_story_id = response['id']
            print(f"   Created story with ID: {self.created_story_id}")
        return success, response

    def test_create_story_anonymous(self):
        """Test creating a story without author (should default to Anonymous)"""
        test_story = {
            "title": f"Anonymous Friend Story {datetime.now().strftime('%H:%M:%S')}",
            "content": "This is a test story without an author to verify default behavior in the friends circle."
        }
        
        success, response = self.run_test("Create Anonymous Friend Story", "POST", "stories", 201, data=test_story)
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

    def test_invite_friends_single(self):
        """Test inviting a single friend"""
        test_email = f"friend_{uuid.uuid4().hex[:8]}@example.com"
        invite_data = {
            "emails": [test_email],
            "message": "Join my Acta Diurna circle!"
        }
        
        success, response = self.run_test("Invite Single Friend", "POST", "invite-friends", 200, data=invite_data)
        if success and response.get('sent_count') == 1:
            print("✅ Single friend invitation sent successfully")
        elif success:
            print(f"⚠️  Expected sent_count=1, got {response.get('sent_count')}")
        return success, response

    def test_invite_friends_multiple(self):
        """Test inviting multiple friends"""
        test_emails = [
            f"friend1_{uuid.uuid4().hex[:8]}@example.com",
            f"friend2_{uuid.uuid4().hex[:8]}@example.com",
            f"friend3_{uuid.uuid4().hex[:8]}@example.com"
        ]
        invite_data = {
            "emails": test_emails,
            "message": "Join our friends circle on Acta Diurna!"
        }
        
        success, response = self.run_test("Invite Multiple Friends", "POST", "invite-friends", 200, data=invite_data)
        if success and response.get('sent_count') == 3:
            print("✅ Multiple friend invitations sent successfully")
        elif success:
            print(f"⚠️  Expected sent_count=3, got {response.get('sent_count')}")
        return success, response

    def test_invite_friends_limit(self):
        """Test inviting more than 50 friends (should fail)"""
        test_emails = [f"friend{i}_{uuid.uuid4().hex[:8]}@example.com" for i in range(51)]
        invite_data = {
            "emails": test_emails,
            "message": "This should fail due to limit"
        }
        
        success, response = self.run_test("Invite Friends - Over Limit", "POST", "invite-friends", 400, data=invite_data)
        return success, response

    def test_invite_friends_invalid_email(self):
        """Test inviting friends with invalid email format"""
        invite_data = {
            "emails": ["invalid-email", "another-invalid"],
            "message": "This should fail due to invalid emails"
        }
        
        success, response = self.run_test("Invite Friends - Invalid Emails", "POST", "invite-friends", 422, data=invite_data)
        return success, response

    def test_subscribe_chronicle(self):
        """Test subscribing to weekly chronicle"""
        test_email = f"subscriber_{uuid.uuid4().hex[:8]}@example.com"
        subscription_data = {"email": test_email}
        
        success, response = self.run_test("Subscribe to Chronicle", "POST", "subscribe", 200, data=subscription_data)
        return success, response

    def test_duplicate_subscription(self):
        """Test duplicate email subscription (should fail)"""
        test_email = f"duplicate_{uuid.uuid4().hex[:8]}@example.com"
        subscription_data = {"email": test_email}
        
        # First subscription should succeed
        success1, _ = self.run_test("First Chronicle Subscription", "POST", "subscribe", 200, data=subscription_data)
        
        # Second subscription should fail
        success2, _ = self.run_test("Duplicate Chronicle Subscription", "POST", "subscribe", 400, data=subscription_data)
        
        return success1 and success2

    def test_flipbook_endpoint(self):
        """Test the flipbook chronicle endpoint - should contain Acta Diurna branding"""
        success, response = self.run_test("Get Flipbook Chronicle", "GET", "newspaper/flipbook", 200)
        if success and isinstance(response, str):
            if "Acta Diurna" in response and "Weekly Chronicle" in response:
                print("✅ Flipbook HTML contains expected Acta Diurna branding")
            elif "Weekly Chronicle" in response:
                print("✅ Flipbook HTML contains Weekly Chronicle")
            else:
                print("⚠️  Flipbook response doesn't contain expected branding")
        return success

    def test_get_subscribers(self):
        """Test getting all chronicle subscribers (admin endpoint)"""
        return self.run_test("Get All Chronicle Subscribers", "GET", "subscribers", 200)

    def test_send_newsletter_manually(self):
        """Test manually triggering chronicle sending"""
        return self.run_test("Send Chronicle Manually", "POST", "newsletter/send", 200)

    # NEW DRAFT MANAGEMENT TESTS
    def test_create_draft(self):
        """Test creating a new draft with rich text content"""
        test_draft = {
            "title": f"Draft Story {datetime.now().strftime('%H:%M:%S')}",
            "content": "<p>This is a <strong>bold</strong> test draft with <em>italic</em> and <u>underlined</u> text.</p>",
            "author": "Test Author"
        }
        
        success, response = self.run_test("Create Draft", "POST", "drafts", 201, data=test_draft)
        if success and 'id' in response:
            self.created_draft_id = response['id']
            print(f"   Created draft with ID: {self.created_draft_id}")
            # Verify rich text content is preserved
            if "<strong>" in response.get('content', '') and "<em>" in response.get('content', ''):
                print("✅ Rich text HTML formatting preserved in draft")
            else:
                print("⚠️  Rich text formatting may not be preserved")
        return success, response

    def test_get_drafts(self):
        """Test getting all saved drafts"""
        return self.run_test("Get All Drafts", "GET", "drafts", 200)

    def test_update_draft(self):
        """Test updating an existing draft"""
        if not self.created_draft_id:
            print("⚠️  No draft ID available for update test")
            return False, {}
            
        updated_draft = {
            "title": f"Updated Draft {datetime.now().strftime('%H:%M:%S')}",
            "content": "<p>Updated content with <strong>new formatting</strong> and <em>different styles</em>.</p>",
            "author": "Updated Author"
        }
        
        success, response = self.run_test("Update Draft", "PUT", f"drafts/{self.created_draft_id}", 200, data=updated_draft)
        if success:
            # Verify updated_at timestamp changed
            if 'updated_at' in response:
                print("✅ Draft updated_at timestamp present")
            else:
                print("⚠️  Draft updated_at timestamp missing")
        return success, response

    def test_delete_draft(self):
        """Test deleting a draft"""
        if not self.created_draft_id:
            print("⚠️  No draft ID available for delete test")
            return False, {}
            
        success, response = self.run_test("Delete Draft", "DELETE", f"drafts/{self.created_draft_id}", 200)
        return success, response

    def test_draft_not_found(self):
        """Test accessing non-existent draft"""
        fake_id = str(uuid.uuid4())
        success, response = self.run_test("Get Non-existent Draft", "GET", f"drafts/{fake_id}", 404)
        return success, response

    def test_create_draft_validation(self):
        """Test draft creation with missing fields"""
        # Test empty draft (should still work as drafts can be minimal)
        minimal_draft = {
            "title": "",
            "content": "",
            "author": ""
        }
        success, _ = self.run_test("Create Minimal Draft", "POST", "drafts", 201, data=minimal_draft)
        return success

    def run_all_tests(self):
        """Run all API tests for Acta Diurna"""
        print("🚀 Starting Acta Diurna API Tests")
        print("📜 Testing Friends-Focused Chronicle Platform")
        print("=" * 60)
        
        # Basic connectivity tests
        self.test_root_endpoint()
        
        # Story-related tests (friends focus)
        self.test_get_stories()
        self.test_get_weekly_stories()
        self.test_create_story()
        self.test_create_story_anonymous()
        self.test_create_story_validation()
        
        # NEW: Invite friends functionality tests (PRIORITY)
        print("\n🎯 PRIORITY: Testing Invite Friends Functionality")
        print("-" * 50)
        self.test_invite_friends_single()
        self.test_invite_friends_multiple()
        self.test_invite_friends_limit()
        self.test_invite_friends_invalid_email()
        
        # Chronicle subscription tests
        print("\n📧 Testing Chronicle Subscription")
        print("-" * 40)
        self.test_subscribe_chronicle()
        self.test_duplicate_subscription()
        self.test_get_subscribers()
        
        # Flipbook chronicle test
        print("\n📖 Testing Weekly Chronicle")
        print("-" * 30)
        self.test_flipbook_endpoint()
        
        # Newsletter functionality
        self.test_send_newsletter_manually()
        
        # Print final results
        print("\n" + "=" * 60)
        print(f"📊 Test Results: {self.tests_passed}/{self.tests_run} tests passed")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All Acta Diurna API tests passed!")
            return 0
        else:
            print(f"❌ {self.tests_run - self.tests_passed} tests failed")
            return 1

def main():
    tester = ActaDiurnaAPITester()
    return tester.run_all_tests()

if __name__ == "__main__":
    sys.exit(main())
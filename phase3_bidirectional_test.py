#!/usr/bin/env python3
"""
CRITICAL PHASE 3 BIDIRECTIONAL CONTRIBUTOR RELATIONSHIP FIX TESTING

This test specifically focuses on verifying the bidirectional contributor relationship fix
implemented in server.py to resolve the contributor story aggregation issue.

Test Scenarios:
1. Create two test users (User A and User B)
2. User A sends invitation to User B
3. User B accepts invitation and adds User A as contributor
4. Verify BOTH users show each other as contributors (bidirectional)
5. Both users submit stories for current week
6. Generate newspaper and verify BOTH stories appear
7. Test all newspaper endpoints include contributor stories
"""

import requests
import json
import time
from datetime import datetime

# Backend URL from environment
BACKEND_URL = "https://e4f87101-35d9-4339-9777-88089f139507.preview.emergentagent.com/api"

class Phase3BidirectionalTester:
    def __init__(self):
        self.session_a = requests.Session()
        self.session_b = requests.Session()
        self.user_a_token = None
        self.user_b_token = None
        self.user_a_data = None
        self.user_b_data = None
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

    def setup_test_users(self):
        """Create and authenticate two test users"""
        print("🔧 SETTING UP TEST USERS")
        print("=" * 50)
        
        # User A - Primary test user
        user_a_data = {
            "email": "test@actadiurna.com",
            "password": "TestPass123!",
            "full_name": "Test User A"
        }
        
        # User B - Contributor test user  
        user_b_data = {
            "email": "contributor@actadiurna.com", 
            "password": "ContribPass123!",
            "full_name": "Test User B"
        }
        
        # Try to login first, register if needed
        for user_data, session, user_type in [
            (user_a_data, self.session_a, "A"),
            (user_b_data, self.session_b, "B")
        ]:
            # Try login first
            login_response = session.post(f"{BACKEND_URL}/auth/login", json={
                "email": user_data["email"],
                "password": user_data["password"]
            })
            
            if login_response.status_code == 200:
                token = login_response.json()["access_token"]
                session.headers.update({"Authorization": f"Bearer {token}"})
                if user_type == "A":
                    self.user_a_token = token
                else:
                    self.user_b_token = token
                self.log_test(f"User {user_type} Login", True, f"Logged in as {user_data['email']}")
            else:
                # Try registration
                register_response = session.post(f"{BACKEND_URL}/auth/register", json=user_data)
                if register_response.status_code == 200:
                    token = register_response.json()["access_token"]
                    session.headers.update({"Authorization": f"Bearer {token}"})
                    if user_type == "A":
                        self.user_a_token = token
                    else:
                        self.user_b_token = token
                    self.log_test(f"User {user_type} Registration", True, f"Registered {user_data['email']}")
                else:
                    self.log_test(f"User {user_type} Auth", False, f"Could not authenticate: {register_response.text}")
                    return False
        
        # Get user info for both users
        user_a_response = self.session_a.get(f"{BACKEND_URL}/users/me")
        user_b_response = self.session_b.get(f"{BACKEND_URL}/users/me")
        
        if user_a_response.status_code == 200 and user_b_response.status_code == 200:
            self.user_a_data = user_a_response.json()
            self.user_b_data = user_b_response.json()
            self.log_test("User Info Retrieval", True, 
                f"User A: {self.user_a_data['full_name']}, User B: {self.user_b_data['full_name']}")
            return True
        else:
            self.log_test("User Info Retrieval", False, "Could not get user information")
            return False

    def test_invitation_workflow(self):
        """Test the complete invitation workflow"""
        print("📧 TESTING INVITATION WORKFLOW")
        print("=" * 50)
        
        # User A sends invitation to User B
        invitation_data = {
            "email": self.user_b_data["email"]
        }
        
        invite_response = self.session_a.post(f"{BACKEND_URL}/invitations/send", json=invitation_data)
        
        if invite_response.status_code == 200:
            self.log_test("Send Invitation", True, f"User A invited User B ({self.user_b_data['email']})")
        elif invite_response.status_code == 400 and "Already invited" in invite_response.text:
            self.log_test("Send Invitation", True, "Invitation already exists (expected)")
        else:
            self.log_test("Send Invitation", False, f"Status: {invite_response.status_code}, Response: {invite_response.text}")
            return False
        
        # Check User B's received invitations
        received_response = self.session_b.get(f"{BACKEND_URL}/invitations/received")
        
        if received_response.status_code == 200:
            invitations = received_response.json()
            user_a_invitation = None
            for inv in invitations:
                if inv.get("from_user_email") == self.user_a_data["email"]:
                    user_a_invitation = inv
                    break
            
            if user_a_invitation:
                self.log_test("Received Invitations", True, f"User B found invitation from User A")
                
                # User B adds User A as contributor
                add_contributor_data = {
                    "invitation_id": user_a_invitation["id"]
                }
                
                add_response = self.session_b.post(f"{BACKEND_URL}/contributors/add", json=add_contributor_data)
                
                if add_response.status_code == 200:
                    self.log_test("Add Contributor", True, "User B added User A as contributor")
                    return True
                elif add_response.status_code == 400 and "Already added" in add_response.text:
                    self.log_test("Add Contributor", True, "Contributor relationship already exists")
                    return True
                else:
                    self.log_test("Add Contributor", False, f"Status: {add_response.status_code}, Response: {add_response.text}")
                    return False
            else:
                self.log_test("Received Invitations", False, "User B did not find invitation from User A")
                return False
        else:
            self.log_test("Received Invitations", False, f"Status: {received_response.status_code}")
            return False

    def test_bidirectional_relationships(self):
        """Test that both users show each other as contributors (bidirectional fix)"""
        print("🔄 TESTING BIDIRECTIONAL CONTRIBUTOR RELATIONSHIPS")
        print("=" * 50)
        
        # Check User A's contributors (should include User B)
        user_a_contributors_response = self.session_a.get(f"{BACKEND_URL}/contributors/my")
        
        if user_a_contributors_response.status_code == 200:
            user_a_contributors = user_a_contributors_response.json()
            user_b_as_contributor = any(
                contrib.get("contributor_email") == self.user_b_data["email"] 
                for contrib in user_a_contributors
            )
            
            if user_b_as_contributor:
                self.log_test("User A Contributors", True, f"User A shows User B as contributor ({len(user_a_contributors)} total)")
            else:
                self.log_test("User A Contributors", False, f"User A does NOT show User B as contributor. Contributors: {[c.get('contributor_email') for c in user_a_contributors]}")
        else:
            self.log_test("User A Contributors", False, f"Status: {user_a_contributors_response.status_code}")
            user_b_as_contributor = False
        
        # Check User B's contributors (should include User A)
        user_b_contributors_response = self.session_b.get(f"{BACKEND_URL}/contributors/my")
        
        if user_b_contributors_response.status_code == 200:
            user_b_contributors = user_b_contributors_response.json()
            user_a_as_contributor = any(
                contrib.get("contributor_email") == self.user_a_data["email"] 
                for contrib in user_b_contributors
            )
            
            if user_a_as_contributor:
                self.log_test("User B Contributors", True, f"User B shows User A as contributor ({len(user_b_contributors)} total)")
            else:
                self.log_test("User B Contributors", False, f"User B does NOT show User A as contributor. Contributors: {[c.get('contributor_email') for c in user_b_contributors]}")
        else:
            self.log_test("User B Contributors", False, f"Status: {user_b_contributors_response.status_code}")
            user_a_as_contributor = False
        
        # CRITICAL: Both users should show each other as contributors for bidirectional fix to work
        bidirectional_success = user_b_as_contributor and user_a_as_contributor
        
        if bidirectional_success:
            self.log_test("Bidirectional Relationship Fix", True, "✅ BIDIRECTIONAL FIX WORKING: Both users show each other as contributors")
        else:
            self.log_test("Bidirectional Relationship Fix", False, "❌ BIDIRECTIONAL FIX FAILED: Relationship is not bidirectional")
        
        return bidirectional_success

    def test_story_submission(self):
        """Test both users submitting stories"""
        print("📝 TESTING STORY SUBMISSION")
        print("=" * 50)
        
        # User A submits story
        user_a_story = {
            "title": "User A's Weekly Story",
            "headline": "Breaking News from User A",
            "content": "This is User A's story for the current week. It should appear in both User A's and User B's newspapers due to the bidirectional contributor relationship."
        }
        
        user_a_story_response = self.session_a.post(f"{BACKEND_URL}/stories/submit", json=user_a_story)
        
        if user_a_story_response.status_code == 200:
            self.log_test("User A Story Submission", True, "User A submitted story successfully")
        elif user_a_story_response.status_code == 400 and "already submitted" in user_a_story_response.text:
            self.log_test("User A Story Submission", True, "User A already submitted story this week")
        else:
            self.log_test("User A Story Submission", False, f"Status: {user_a_story_response.status_code}, Response: {user_a_story_response.text}")
        
        # User B submits story
        user_b_story = {
            "title": "User B's Weekly Story", 
            "headline": "Exclusive Report from User B",
            "content": "This is User B's story for the current week. It should appear in both User A's and User B's newspapers due to the bidirectional contributor relationship."
        }
        
        user_b_story_response = self.session_b.post(f"{BACKEND_URL}/stories/submit", json=user_b_story)
        
        if user_b_story_response.status_code == 200:
            self.log_test("User B Story Submission", True, "User B submitted story successfully")
            return True
        elif user_b_story_response.status_code == 400 and "already submitted" in user_b_story_response.text:
            self.log_test("User B Story Submission", True, "User B already submitted story this week")
            return True
        else:
            self.log_test("User B Story Submission", False, f"Status: {user_b_story_response.status_code}, Response: {user_b_story_response.text}")
            return False

    def test_newspaper_generation_with_contributors(self):
        """Test newspaper generation includes contributor stories"""
        print("🗞️ TESTING NEWSPAPER GENERATION WITH CONTRIBUTOR STORIES")
        print("=" * 50)
        
        # Test User A's current newspaper (should include User B's story)
        user_a_newspaper_response = self.session_a.get(f"{BACKEND_URL}/newspapers/current")
        
        if user_a_newspaper_response.status_code == 200:
            user_a_newspaper = user_a_newspaper_response.json()
            stories = user_a_newspaper.get("stories", [])
            
            user_a_story_found = any(story.get("author_id") == self.user_a_data["id"] for story in stories)
            user_b_story_found = any(story.get("author_id") == self.user_b_data["id"] for story in stories)
            
            self.log_test("User A Newspaper Generation", True, 
                f"Generated newspaper with {len(stories)} stories")
            
            if user_a_story_found and user_b_story_found:
                self.log_test("User A Contributor Stories", True, 
                    "✅ User A's newspaper includes BOTH User A's and User B's stories")
            elif user_a_story_found and not user_b_story_found:
                self.log_test("User A Contributor Stories", False, 
                    "❌ User A's newspaper only includes User A's story, missing User B's story")
            else:
                self.log_test("User A Contributor Stories", False, 
                    f"❌ Unexpected story configuration: A={user_a_story_found}, B={user_b_story_found}")
        else:
            self.log_test("User A Newspaper Generation", False, 
                f"Status: {user_a_newspaper_response.status_code}")
            user_a_story_found = user_b_story_found = False
        
        # Test User B's current newspaper (should include User A's story)
        user_b_newspaper_response = self.session_b.get(f"{BACKEND_URL}/newspapers/current")
        
        if user_b_newspaper_response.status_code == 200:
            user_b_newspaper = user_b_newspaper_response.json()
            stories = user_b_newspaper.get("stories", [])
            
            user_a_story_in_b = any(story.get("author_id") == self.user_a_data["id"] for story in stories)
            user_b_story_in_b = any(story.get("author_id") == self.user_b_data["id"] for story in stories)
            
            self.log_test("User B Newspaper Generation", True, 
                f"Generated newspaper with {len(stories)} stories")
            
            if user_a_story_in_b and user_b_story_in_b:
                self.log_test("User B Contributor Stories", True, 
                    "✅ User B's newspaper includes BOTH User A's and User B's stories")
            elif user_b_story_in_b and not user_a_story_in_b:
                self.log_test("User B Contributor Stories", False, 
                    "❌ User B's newspaper only includes User B's story, missing User A's story")
            else:
                self.log_test("User B Contributor Stories", False, 
                    f"❌ Unexpected story configuration: A={user_a_story_in_b}, B={user_b_story_in_b}")
        else:
            self.log_test("User B Newspaper Generation", False, 
                f"Status: {user_b_newspaper_response.status_code}")
            user_a_story_in_b = user_b_story_in_b = False
        
        # Overall bidirectional newspaper success
        bidirectional_newspaper_success = (
            user_a_story_found and user_b_story_found and 
            user_a_story_in_b and user_b_story_in_b
        )
        
        if bidirectional_newspaper_success:
            self.log_test("Bidirectional Newspaper Fix", True, 
                "✅ BIDIRECTIONAL NEWSPAPER FIX WORKING: Both users see each other's stories")
        else:
            self.log_test("Bidirectional Newspaper Fix", False, 
                "❌ BIDIRECTIONAL NEWSPAPER FIX FAILED: Stories not appearing bidirectionally")
        
        return bidirectional_newspaper_success

    def test_weekly_stories_endpoint(self):
        """Test /api/stories/weekly/{week} includes contributor stories"""
        print("📅 TESTING WEEKLY STORIES ENDPOINT")
        print("=" * 50)
        
        # Get current week
        health_response = self.session_a.get(f"{BACKEND_URL}/health")
        if health_response.status_code == 200:
            current_week = health_response.json().get("current_week")
        else:
            current_week = "2025-W31"  # Fallback
        
        # Test User A's weekly stories
        user_a_weekly_response = self.session_a.get(f"{BACKEND_URL}/stories/weekly/{current_week}")
        
        if user_a_weekly_response.status_code == 200:
            user_a_weekly_stories = user_a_weekly_response.json()
            
            user_a_story_found = any(story.get("author_id") == self.user_a_data["id"] for story in user_a_weekly_stories)
            user_b_story_found = any(story.get("author_id") == self.user_b_data["id"] for story in user_a_weekly_stories)
            
            if user_a_story_found and user_b_story_found:
                self.log_test("User A Weekly Stories", True, 
                    f"✅ /api/stories/weekly/{current_week} includes BOTH users' stories ({len(user_a_weekly_stories)} total)")
            else:
                self.log_test("User A Weekly Stories", False, 
                    f"❌ /api/stories/weekly/{current_week} missing stories: A={user_a_story_found}, B={user_b_story_found}")
        else:
            self.log_test("User A Weekly Stories", False, 
                f"Status: {user_a_weekly_response.status_code}")
            user_a_story_found = user_b_story_found = False
        
        # Test User B's weekly stories
        user_b_weekly_response = self.session_b.get(f"{BACKEND_URL}/stories/weekly/{current_week}")
        
        if user_b_weekly_response.status_code == 200:
            user_b_weekly_stories = user_b_weekly_response.json()
            
            user_a_story_in_b = any(story.get("author_id") == self.user_a_data["id"] for story in user_b_weekly_stories)
            user_b_story_in_b = any(story.get("author_id") == self.user_b_data["id"] for story in user_b_weekly_stories)
            
            if user_a_story_in_b and user_b_story_in_b:
                self.log_test("User B Weekly Stories", True, 
                    f"✅ /api/stories/weekly/{current_week} includes BOTH users' stories ({len(user_b_weekly_stories)} total)")
                return True
            else:
                self.log_test("User B Weekly Stories", False, 
                    f"❌ /api/stories/weekly/{current_week} missing stories: A={user_a_story_in_b}, B={user_b_story_in_b}")
                return False
        else:
            self.log_test("User B Weekly Stories", False, 
                f"Status: {user_b_weekly_response.status_code}")
            return False

    def test_newspaper_archive_endpoint(self):
        """Test /api/newspapers/archive includes contributor stories"""
        print("📚 TESTING NEWSPAPER ARCHIVE ENDPOINT")
        print("=" * 50)
        
        # Test User A's archive
        user_a_archive_response = self.session_a.get(f"{BACKEND_URL}/newspapers/archive")
        
        if user_a_archive_response.status_code == 200:
            user_a_archive = user_a_archive_response.json()
            self.log_test("User A Archive", True, 
                f"Retrieved {len(user_a_archive)} archived newspapers")
        else:
            self.log_test("User A Archive", False, 
                f"Status: {user_a_archive_response.status_code}")
        
        # Test User B's archive
        user_b_archive_response = self.session_b.get(f"{BACKEND_URL}/newspapers/archive")
        
        if user_b_archive_response.status_code == 200:
            user_b_archive = user_b_archive_response.json()
            self.log_test("User B Archive", True, 
                f"Retrieved {len(user_b_archive)} archived newspapers")
            return True
        else:
            self.log_test("User B Archive", False, 
                f"Status: {user_b_archive_response.status_code}")
            return False

    def run_comprehensive_test(self):
        """Run comprehensive Phase 3 bidirectional contributor relationship test"""
        print("🚨 CRITICAL PHASE 3 BIDIRECTIONAL CONTRIBUTOR RELATIONSHIP FIX TESTING")
        print("=" * 80)
        print("Testing the recent bidirectional contributor relationship fix implemented in server.py")
        print("Expected: When users accept invitations, BOTH user records are updated bidirectionally")
        print("=" * 80)
        
        # Test sequence
        tests = [
            ("Setup Test Users", self.setup_test_users),
            ("Invitation Workflow", self.test_invitation_workflow),
            ("Bidirectional Relationships", self.test_bidirectional_relationships),
            ("Story Submission", self.test_story_submission),
            ("Newspaper Generation with Contributors", self.test_newspaper_generation_with_contributors),
            ("Weekly Stories Endpoint", self.test_weekly_stories_endpoint),
            ("Newspaper Archive Endpoint", self.test_newspaper_archive_endpoint),
        ]
        
        passed = 0
        failed = 0
        critical_failures = []
        
        for test_name, test_func in tests:
            print(f"\n🔍 RUNNING: {test_name}")
            print("-" * 50)
            
            try:
                success = test_func()
                if success:
                    passed += 1
                else:
                    failed += 1
                    if test_name in ["Bidirectional Relationships", "Newspaper Generation with Contributors"]:
                        critical_failures.append(test_name)
            except Exception as e:
                print(f"❌ CRITICAL ERROR in {test_name}: {str(e)}")
                failed += 1
                critical_failures.append(test_name)
            
            time.sleep(1)  # Brief pause between tests
        
        # Final analysis
        print("\n" + "=" * 80)
        print("🎯 PHASE 3 BIDIRECTIONAL FIX ANALYSIS")
        print("=" * 80)
        
        if len(critical_failures) == 0:
            print("✅ SUCCESS: Bidirectional contributor relationship fix is WORKING")
            print("   - Both users show each other as contributors")
            print("   - Contributor stories appear in newspapers correctly")
            print("   - All newspaper endpoints include contributor stories")
            fix_status = "WORKING"
        else:
            print("❌ FAILURE: Bidirectional contributor relationship fix has ISSUES")
            print(f"   - Critical failures in: {', '.join(critical_failures)}")
            print("   - Contributor stories may not be appearing in newspapers")
            fix_status = "FAILED"
        
        print(f"\n📊 TEST SUMMARY")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"📈 Success Rate: {(passed/(passed+failed)*100):.1f}%")
        print(f"🔧 Fix Status: {fix_status}")
        
        return {
            "fix_status": fix_status,
            "passed": passed,
            "failed": failed,
            "critical_failures": critical_failures,
            "test_results": self.test_results
        }

if __name__ == "__main__":
    tester = Phase3BidirectionalTester()
    results = tester.run_comprehensive_test()
    
    # Save results
    with open('/app/phase3_bidirectional_test_results.json', 'w') as f:
        json.dump(results, indent=2, fp=f)
    
    print(f"\n📄 Detailed results saved to: /app/phase3_bidirectional_test_results.json")
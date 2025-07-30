#!/usr/bin/env python3
"""
COMPREHENSIVE PHASE 3 BIDIRECTIONAL TESTING - FINAL VERIFICATION
Tests all critical fixes as requested in the review
"""

import requests
import json
import time
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = "https://464d35f9-1da6-4f46-92d7-fc7b50272fb2.preview.emergentagent.com/api"

class FinalPhase3Tester:
    def __init__(self):
        self.session_a = requests.Session()
        self.session_b = requests.Session()
        self.user_a_token = None
        self.user_b_token = None
        self.user_a_data = None
        self.user_b_data = None
        self.test_results = []
        self.current_week = None
        
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
        """Setup two test users as specified in the review"""
        print("🔧 SETTING UP TEST USERS")
        print("=" * 50)
        
        # User A: test@actadiurna.com / TestPass123!
        user_a_data = {
            "email": "test@actadiurna.com",
            "password": "TestPass123!",
            "full_name": "Test User A"
        }
        
        # User B: contributor@actadiurna.com / ContribPass123!
        user_b_data = {
            "email": "contributor@actadiurna.com", 
            "password": "ContribPass123!",
            "full_name": "Contributor User B"
        }
        
        # Try to login first, register if needed
        for user_data, session, user_type in [
            (user_a_data, self.session_a, "User A"),
            (user_b_data, self.session_b, "User B")
        ]:
            # Try login first
            login_response = session.post(f"{BACKEND_URL}/auth/login", json={
                "email": user_data["email"],
                "password": user_data["password"]
            })
            
            if login_response.status_code == 200:
                token = login_response.json()["access_token"]
                session.headers.update({"Authorization": f"Bearer {token}"})
                if user_type == "User A":
                    self.user_a_token = token
                else:
                    self.user_b_token = token
                self.log_test(f"Setup {user_type}", True, f"Logged in as {user_data['email']}")
            else:
                # Try registration
                register_response = session.post(f"{BACKEND_URL}/auth/register", json=user_data)
                
                if register_response.status_code == 200:
                    token = register_response.json()["access_token"]
                    session.headers.update({"Authorization": f"Bearer {token}"})
                    if user_type == "User A":
                        self.user_a_token = token
                    else:
                        self.user_b_token = token
                    self.log_test(f"Setup {user_type}", True, f"Registered and logged in as {user_data['email']}")
                else:
                    self.log_test(f"Setup {user_type}", False, f"Could not register/login: {register_response.text}")
                    return False
        
        # Get user info for both users
        user_a_response = self.session_a.get(f"{BACKEND_URL}/users/me")
        user_b_response = self.session_b.get(f"{BACKEND_URL}/users/me")
        
        if user_a_response.status_code == 200 and user_b_response.status_code == 200:
            self.user_a_data = user_a_response.json()
            self.user_b_data = user_b_response.json()
            self.log_test("Get User Info", True, f"User A ID: {self.user_a_data['id']}, User B ID: {self.user_b_data['id']}")
            return True
        else:
            self.log_test("Get User Info", False, "Could not retrieve user information")
            return False

    def get_current_week(self):
        """Get current week from health endpoint"""
        health_response = self.session_a.get(f"{BACKEND_URL}/health")
        if health_response.status_code == 200:
            self.current_week = health_response.json().get("current_week")
            self.log_test("Get Current Week", True, f"Current week: {self.current_week}")
            return True
        else:
            self.log_test("Get Current Week", False, "Could not get current week")
            return False

    def test_invitation_workflow(self):
        """Test the complete invitation workflow"""
        print("📧 TESTING INVITATION WORKFLOW")
        print("=" * 50)
        
        # User A sends invitation to User B
        invitation_data = {"email": self.user_b_data["email"]}
        invite_response = self.session_a.post(f"{BACKEND_URL}/invitations/send", json=invitation_data)
        
        if invite_response.status_code == 200:
            self.log_test("Send Invitation A->B", True, f"User A sent invitation to {self.user_b_data['email']}")
        elif invite_response.status_code == 400 and "Already invited" in invite_response.text:
            self.log_test("Send Invitation A->B", True, "Invitation already exists (expected)")
        else:
            self.log_test("Send Invitation A->B", False, f"Status: {invite_response.status_code}, Response: {invite_response.text}")
        
        # User B sends invitation to User A (for bidirectional testing)
        invitation_data_b = {"email": self.user_a_data["email"]}
        invite_response_b = self.session_b.post(f"{BACKEND_URL}/invitations/send", json=invitation_data_b)
        
        if invite_response_b.status_code == 200:
            self.log_test("Send Invitation B->A", True, f"User B sent invitation to {self.user_a_data['email']}")
        elif invite_response_b.status_code == 400 and "Already invited" in invite_response_b.text:
            self.log_test("Send Invitation B->A", True, "Invitation already exists (expected)")
        else:
            self.log_test("Send Invitation B->A", False, f"Status: {invite_response_b.status_code}")
        
        # Check received invitations for both users
        received_a = self.session_a.get(f"{BACKEND_URL}/invitations/received")
        received_b = self.session_b.get(f"{BACKEND_URL}/invitations/received")
        
        invitation_a_id = None
        invitation_b_id = None
        
        if received_a.status_code == 200:
            invitations_a = received_a.json()
            for inv in invitations_a:
                if inv.get("from_user_email") == self.user_b_data["email"]:
                    invitation_a_id = inv["id"]
                    break
            self.log_test("Check Received Invitations A", True, f"User A found {len(invitations_a)} invitations")
        
        if received_b.status_code == 200:
            invitations_b = received_b.json()
            for inv in invitations_b:
                if inv.get("from_user_email") == self.user_a_data["email"]:
                    invitation_b_id = inv["id"]
                    break
            self.log_test("Check Received Invitations B", True, f"User B found {len(invitations_b)} invitations")
        
        self.invitation_a_id = invitation_a_id
        self.invitation_b_id = invitation_b_id
        
        return invitation_a_id is not None or invitation_b_id is not None

    def test_bidirectional_contributor_creation(self):
        """Test the critical bidirectional contributor relationship creation"""
        print("🔄 TESTING BIDIRECTIONAL CONTRIBUTOR CREATION")
        print("=" * 50)
        
        # If User A has invitation from User B, accept it
        if self.invitation_a_id:
            contributor_data_a = {"invitation_id": self.invitation_a_id}
            add_response_a = self.session_a.post(f"{BACKEND_URL}/contributors/add", json=contributor_data_a)
            
            if add_response_a.status_code == 200:
                self.log_test("User A Add Contributor", True, "User A added User B as contributor")
            elif add_response_a.status_code == 400 and "already exists" in add_response_a.text:
                self.log_test("User A Add Contributor", True, "Relationship already exists (expected)")
            else:
                self.log_test("User A Add Contributor", False, f"Status: {add_response_a.status_code}, Response: {add_response_a.text}")
        
        # If User B has invitation from User A, accept it
        if self.invitation_b_id:
            contributor_data_b = {"invitation_id": self.invitation_b_id}
            add_response_b = self.session_b.post(f"{BACKEND_URL}/contributors/add", json=contributor_data_b)
            
            if add_response_b.status_code == 200:
                self.log_test("User B Add Contributor", True, "User B added User A as contributor")
            elif add_response_b.status_code == 400 and "already exists" in add_response_b.text:
                self.log_test("User B Add Contributor", True, "Relationship already exists (expected)")
            else:
                self.log_test("User B Add Contributor", False, f"Status: {add_response_b.status_code}, Response: {add_response_b.text}")
        
        # CRITICAL TEST: Check if BOTH users show each other as contributors
        print("🔍 VERIFYING BIDIRECTIONAL RELATIONSHIPS")
        
        # User A's contributors (should include User B)
        user_a_contributors_response = self.session_a.get(f"{BACKEND_URL}/contributors/my")
        user_a_contributors = []
        user_b_in_a_contributors = False
        
        if user_a_contributors_response.status_code == 200:
            user_a_contributors = user_a_contributors_response.json()
            user_b_in_a_contributors = any(c.get("contributor_id") == self.user_b_data["id"] for c in user_a_contributors)
            
            if user_b_in_a_contributors:
                self.log_test("User A Contributors Check", True, f"User A shows User B as contributor ({len(user_a_contributors)} total)")
            else:
                self.log_test("User A Contributors Check", False, f"User A does NOT show User B as contributor. Contributors: {[c.get('contributor_name') for c in user_a_contributors]}")
        else:
            self.log_test("User A Contributors Check", False, f"Status: {user_a_contributors_response.status_code}")
        
        # User B's contributors (should include User A)
        user_b_contributors_response = self.session_b.get(f"{BACKEND_URL}/contributors/my")
        user_b_contributors = []
        user_a_in_b_contributors = False
        
        if user_b_contributors_response.status_code == 200:
            user_b_contributors = user_b_contributors_response.json()
            user_a_in_b_contributors = any(c.get("contributor_id") == self.user_a_data["id"] for c in user_b_contributors)
            
            if user_a_in_b_contributors:
                self.log_test("User B Contributors Check", True, f"User B shows User A as contributor ({len(user_b_contributors)} total)")
            else:
                self.log_test("User B Contributors Check", False, f"User B does NOT show User A as contributor. Contributors: {[c.get('contributor_name') for c in user_b_contributors]}")
        else:
            self.log_test("User B Contributors Check", False, f"Status: {user_b_contributors_response.status_code}")
        
        # CRITICAL VERIFICATION: Check if bidirectional relationships exist
        bidirectional_success = user_b_in_a_contributors and user_a_in_b_contributors
        
        if bidirectional_success:
            self.log_test("Bidirectional Relationship Verification", True, "TRUE bidirectional relationships confirmed - both users show each other as contributors")
            return True
        else:
            self.log_test("Bidirectional Relationship Verification", False, "BIDIRECTIONAL RELATIONSHIP NOT IMPLEMENTED - relationships are not bidirectional")
            return False

    def test_weekly_stories_endpoint(self):
        """Test the new /api/stories/weekly/{week} endpoint"""
        print("📅 TESTING WEEKLY STORIES ENDPOINT")
        print("=" * 50)
        
        # Test endpoint exists and returns data for User A
        weekly_stories_response_a = self.session_a.get(f"{BACKEND_URL}/stories/weekly/{self.current_week}")
        
        if weekly_stories_response_a.status_code == 200:
            stories_a = weekly_stories_response_a.json()
            if isinstance(stories_a, list):
                self.log_test("Weekly Stories Endpoint A", True, f"User A sees {len(stories_a)} stories for {self.current_week}")
                for story in stories_a:
                    print(f"   - {story.get('title')} by {story.get('author_name')}")
            else:
                self.log_test("Weekly Stories Endpoint A", False, f"Endpoint returns non-list data: {type(stories_a)}")
                return False
        else:
            self.log_test("Weekly Stories Endpoint A", False, f"Status: {weekly_stories_response_a.status_code}")
            return False
        
        # Test endpoint for User B
        weekly_stories_response_b = self.session_b.get(f"{BACKEND_URL}/stories/weekly/{self.current_week}")
        
        if weekly_stories_response_b.status_code == 200:
            stories_b = weekly_stories_response_b.json()
            if isinstance(stories_b, list):
                self.log_test("Weekly Stories Endpoint B", True, f"User B sees {len(stories_b)} stories for {self.current_week}")
                for story in stories_b:
                    print(f"   - {story.get('title')} by {story.get('author_name')}")
                return True
            else:
                self.log_test("Weekly Stories Endpoint B", False, f"Endpoint returns non-list data: {type(stories_b)}")
                return False
        else:
            self.log_test("Weekly Stories Endpoint B", False, f"Status: {weekly_stories_response_b.status_code}")
            return False

    def test_story_submission_and_aggregation(self):
        """Test story submission from both users and verify aggregation"""
        print("📝 TESTING STORY SUBMISSION AND AGGREGATION")
        print("=" * 50)
        
        # User A submits a story
        user_a_story = {
            "title": "User A's Test Story",
            "headline": "Breaking News from User A",
            "content": "This is User A's story for the current week. It should appear in both User A's and User B's newspapers due to bidirectional contributor relationships."
        }
        
        story_a_response = self.session_a.post(f"{BACKEND_URL}/stories/submit", json=user_a_story)
        
        if story_a_response.status_code == 200:
            self.log_test("User A Story Submission", True, "User A submitted story successfully")
        elif story_a_response.status_code == 400 and "already submitted" in story_a_response.text:
            self.log_test("User A Story Submission", True, "User A already submitted story this week (expected)")
        else:
            self.log_test("User A Story Submission", False, f"Status: {story_a_response.status_code}, Response: {story_a_response.text}")
        
        # User B submits a story
        user_b_story = {
            "title": "User B's Test Story", 
            "headline": "Exclusive Report from User B",
            "content": "This is User B's story for the current week. It should appear in both User A's and User B's newspapers due to bidirectional contributor relationships."
        }
        
        story_b_response = self.session_b.post(f"{BACKEND_URL}/stories/submit", json=user_b_story)
        
        if story_b_response.status_code == 200:
            self.log_test("User B Story Submission", True, "User B submitted story successfully")
        elif story_b_response.status_code == 400 and "already submitted" in story_b_response.text:
            self.log_test("User B Story Submission", True, "User B already submitted story this week (expected)")
        else:
            self.log_test("User B Story Submission", False, f"Status: {story_b_response.status_code}, Response: {story_b_response.text}")
        
        return True

    def test_newspaper_generation_with_contributors(self):
        """Test newspaper generation includes contributor stories"""
        print("🗞️ TESTING NEWSPAPER GENERATION WITH CONTRIBUTORS")
        print("=" * 50)
        
        # Test User A's newspaper
        user_a_newspaper_response = self.session_a.get(f"{BACKEND_URL}/newspapers/current")
        
        if user_a_newspaper_response.status_code == 200:
            user_a_newspaper = user_a_newspaper_response.json()
            user_a_stories = user_a_newspaper.get("stories", [])
            user_a_story_count = len(user_a_stories)
            
            # Check if User B's story appears in User A's newspaper
            user_b_story_in_a_newspaper = any(story.get("author_id") == self.user_b_data["id"] for story in user_a_stories)
            
            self.log_test("User A Newspaper Generation", True, f"User A's newspaper contains {user_a_story_count} stories")
            for story in user_a_stories:
                print(f"   - {story.get('title')} by {story.get('author_name')} (ID: {story.get('author_id')})")
            
            if user_b_story_in_a_newspaper:
                self.log_test("User A Includes User B Stories", True, "User A's newspaper includes User B's story")
            else:
                self.log_test("User A Includes User B Stories", False, "User A's newspaper does NOT include User B's story")
        else:
            self.log_test("User A Newspaper Generation", False, f"Status: {user_a_newspaper_response.status_code}")
        
        # Test User B's newspaper
        user_b_newspaper_response = self.session_b.get(f"{BACKEND_URL}/newspapers/current")
        
        if user_b_newspaper_response.status_code == 200:
            user_b_newspaper = user_b_newspaper_response.json()
            user_b_stories = user_b_newspaper.get("stories", [])
            user_b_story_count = len(user_b_stories)
            
            # Check if User A's story appears in User B's newspaper
            user_a_story_in_b_newspaper = any(story.get("author_id") == self.user_a_data["id"] for story in user_b_stories)
            
            self.log_test("User B Newspaper Generation", True, f"User B's newspaper contains {user_b_story_count} stories")
            for story in user_b_stories:
                print(f"   - {story.get('title')} by {story.get('author_name')} (ID: {story.get('author_id')})")
            
            if user_a_story_in_b_newspaper:
                self.log_test("User B Includes User A Stories", True, "User B's newspaper includes User A's story")
                return True
            else:
                self.log_test("User B Includes User A Stories", False, "User B's newspaper does NOT include User A's story")
                return False
        else:
            self.log_test("User B Newspaper Generation", False, f"Status: {user_b_newspaper_response.status_code}")
            return False

    def run_comprehensive_phase3_test(self):
        """Run the complete Phase 3 bidirectional test workflow"""
        print("🚀 COMPREHENSIVE PHASE 3 BIDIRECTIONAL TESTING - FINAL VERIFICATION")
        print("=" * 80)
        print("Testing critical fixes as requested in review:")
        print("1. TRUE BIDIRECTIONAL CONTRIBUTOR RELATIONSHIPS - /api/contributors/add should create TWO database records (A->B and B->A)")
        print("2. NEW /api/stories/weekly/{week} ENDPOINT - Should return stories from user and contributors")
        print("3. NEWSPAPER GENERATION WITH CONTRIBUTORS - Should include contributor stories in flipbooks")
        print("=" * 80)
        
        # Step 1: Setup test users
        if not self.setup_test_users():
            print("❌ CRITICAL: Could not setup test users")
            return False
        
        # Step 2: Get current week
        if not self.get_current_week():
            print("❌ CRITICAL: Could not get current week")
            return False
        
        # Step 3: Test invitation workflow
        self.test_invitation_workflow()
        
        # Step 4: Test bidirectional contributor creation (CRITICAL)
        bidirectional_success = self.test_bidirectional_contributor_creation()
        
        # Step 5: Test weekly stories endpoint (CRITICAL)
        weekly_endpoint_success = self.test_weekly_stories_endpoint()
        
        # Step 6: Test story submission and aggregation
        self.test_story_submission_and_aggregation()
        
        # Step 7: Test newspaper generation with contributors (CRITICAL)
        newspaper_generation_success = self.test_newspaper_generation_with_contributors()
        
        # Final analysis
        print("\n" + "=" * 80)
        print("📊 PHASE 3 BIDIRECTIONAL TEST RESULTS")
        print("=" * 80)
        
        critical_fixes_working = (
            bidirectional_success and
            weekly_endpoint_success and
            newspaper_generation_success
        )
        
        if critical_fixes_working:
            print("✅ ALL CRITICAL FIXES VERIFIED WORKING")
            print("   ✓ Bidirectional contributor relationships implemented")
            print("   ✓ Weekly stories endpoint functional")
            print("   ✓ Newspaper generation includes contributor stories")
        else:
            print("❌ CRITICAL FIXES NOT WORKING")
            if not bidirectional_success:
                print("   ❌ Bidirectional contributor relationships NOT implemented")
            if not weekly_endpoint_success:
                print("   ❌ Weekly stories endpoint missing or broken")
            if not newspaper_generation_success:
                print("   ❌ Newspaper generation does NOT include contributor stories")
        
        # Calculate success metrics
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"\n📈 OVERALL RESULTS:")
        print(f"   Tests Passed: {passed_tests}/{total_tests}")
        print(f"   Success Rate: {success_rate:.1f}%")
        print(f"   Critical Fixes Working: {'YES' if critical_fixes_working else 'NO'}")
        
        return critical_fixes_working

if __name__ == "__main__":
    tester = FinalPhase3Tester()
    success = tester.run_comprehensive_phase3_test()
    
    # Save detailed results
    with open('/app/final_phase3_test_results.json', 'w') as f:
        json.dump({
            "critical_fixes_working": success,
            "detailed_results": tester.test_results,
            "summary": {
                "total_tests": len(tester.test_results),
                "passed_tests": sum(1 for r in tester.test_results if r["success"]),
                "success_rate": sum(1 for r in tester.test_results if r["success"]) / len(tester.test_results) * 100 if tester.test_results else 0
            }
        }, f, indent=2)
    
    print(f"\n📄 Detailed results saved to: /app/final_phase3_test_results.json")
    
    if success:
        print("\n🎉 PHASE 3 BIDIRECTIONAL TESTING COMPLETE - ALL CRITICAL FIXES WORKING!")
    else:
        print("\n🚨 PHASE 3 BIDIRECTIONAL TESTING COMPLETE - CRITICAL FIXES STILL NOT WORKING!")
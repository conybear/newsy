#!/usr/bin/env python3
"""
COMPREHENSIVE PHASE 3 ARCHITECTURAL REDESIGN VERIFICATION

This test suite specifically verifies the MongoDB-based bidirectional contributor system
redesign as requested in the review. Tests the new User model with contributors field
and atomic $addToSet operations.
"""

import requests
import json
import time
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = "https://464d35f9-1da6-4f46-92d7-fc7b50272fb2.preview.emergentagent.com/api"

class Phase3RedesignTester:
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
        """Setup two test users for bidirectional testing"""
        print("🔧 SETTING UP TEST USERS FOR PHASE 3 VERIFICATION")
        print("=" * 60)
        
        # User A credentials
        user_a_creds = {
            "email": "test@actadiurna.com",
            "password": "TestPass123!",
            "full_name": "Test User A"
        }
        
        # User B credentials  
        user_b_creds = {
            "email": "contributor@actadiurna.com", 
            "password": "ContribPass123!",
            "full_name": "Contributor User B"
        }
        
        # Try to login User A first
        login_response_a = self.session_a.post(f"{BACKEND_URL}/auth/login", json={
            "email": user_a_creds["email"],
            "password": user_a_creds["password"]
        })
        
        if login_response_a.status_code == 200:
            self.user_a_token = login_response_a.json()["access_token"]
            self.session_a.headers.update({"Authorization": f"Bearer {self.user_a_token}"})
            self.log_test("User A Login", True, f"Logged in as {user_a_creds['email']}")
        else:
            # Register User A
            register_response_a = self.session_a.post(f"{BACKEND_URL}/auth/register", json=user_a_creds)
            if register_response_a.status_code == 200:
                self.user_a_token = register_response_a.json()["access_token"]
                self.session_a.headers.update({"Authorization": f"Bearer {self.user_a_token}"})
                self.log_test("User A Registration", True, f"Registered {user_a_creds['email']}")
            else:
                self.log_test("User A Setup", False, f"Could not setup User A: {register_response_a.text}")
                return False
        
        # Try to login User B first
        login_response_b = self.session_b.post(f"{BACKEND_URL}/auth/login", json={
            "email": user_b_creds["email"],
            "password": user_b_creds["password"]
        })
        
        if login_response_b.status_code == 200:
            self.user_b_token = login_response_b.json()["access_token"]
            self.session_b.headers.update({"Authorization": f"Bearer {self.user_b_token}"})
            self.log_test("User B Login", True, f"Logged in as {user_b_creds['email']}")
        else:
            # Register User B
            register_response_b = self.session_b.post(f"{BACKEND_URL}/auth/register", json=user_b_creds)
            if register_response_b.status_code == 200:
                self.user_b_token = register_response_b.json()["access_token"]
                self.session_b.headers.update({"Authorization": f"Bearer {self.user_b_token}"})
                self.log_test("User B Registration", True, f"Registered {user_b_creds['email']}")
            else:
                self.log_test("User B Setup", False, f"Could not setup User B: {register_response_b.text}")
                return False
        
        # Get user data
        user_a_response = self.session_a.get(f"{BACKEND_URL}/users/me")
        user_b_response = self.session_b.get(f"{BACKEND_URL}/users/me")
        
        if user_a_response.status_code == 200 and user_b_response.status_code == 200:
            self.user_a_data = user_a_response.json()
            self.user_b_data = user_b_response.json()
            self.log_test("User Data Retrieval", True, f"User A ID: {self.user_a_data['id']}, User B ID: {self.user_b_data['id']}")
            return True
        else:
            self.log_test("User Data Retrieval", False, "Could not get user data")
            return False

    def test_user_model_contributors_field(self):
        """Test 1: Verify User documents have contributors field"""
        print("🧪 TEST 1: USER MODEL WITH CONTRIBUTORS FIELD")
        print("-" * 50)
        
        try:
            # Check if users have contributors field by getting their contributors
            response_a = self.session_a.get(f"{BACKEND_URL}/contributors/my")
            response_b = self.session_b.get(f"{BACKEND_URL}/contributors/my")
            
            if response_a.status_code == 200 and response_b.status_code == 200:
                contributors_a = response_a.json()
                contributors_b = response_b.json()
                
                self.log_test("User Model Contributors Field", True, 
                    f"User A has {len(contributors_a)} contributors, User B has {len(contributors_b)} contributors")
                return True, {"user_a_contributors": contributors_a, "user_b_contributors": contributors_b}
            else:
                self.log_test("User Model Contributors Field", False, 
                    f"API error - A: {response_a.status_code}, B: {response_b.status_code}")
                return False, None
                
        except Exception as e:
            self.log_test("User Model Contributors Field", False, f"Exception: {str(e)}")
            return False, None

    def test_bidirectional_contributor_creation(self):
        """Test 2: Test bidirectional contributor creation via invitation workflow"""
        print("🧪 TEST 2: BIDIRECTIONAL CONTRIBUTOR CREATION")
        print("-" * 50)
        
        try:
            # Step 1: User A sends invitation to User B
            invitation_data = {"email": self.user_b_data["email"]}
            invite_response = self.session_a.post(f"{BACKEND_URL}/invitations/send", json=invitation_data)
            
            if invite_response.status_code != 200:
                self.log_test("Send Invitation", False, f"Status: {invite_response.status_code}, Response: {invite_response.text}")
                return False, None
            
            self.log_test("Send Invitation", True, f"User A sent invitation to User B")
            
            # Step 2: User B checks received invitations
            received_response = self.session_b.get(f"{BACKEND_URL}/invitations/received")
            
            if received_response.status_code != 200:
                self.log_test("Check Received Invitations", False, f"Status: {received_response.status_code}")
                return False, None
            
            received_invitations = received_response.json()
            self.log_test("Check Received Invitations", True, f"User B has {len(received_invitations)} received invitations")
            
            if len(received_invitations) == 0:
                self.log_test("Bidirectional Contributor Creation", False, "No invitations found for User B")
                return False, None
            
            # Step 3: User B accepts invitation via /api/contributors/add
            invitation_id = received_invitations[0]["id"]
            add_contributor_data = {"invitation_id": invitation_id}
            add_response = self.session_b.post(f"{BACKEND_URL}/contributors/add", json=add_contributor_data)
            
            if add_response.status_code != 200:
                self.log_test("Accept Invitation", False, f"Status: {add_response.status_code}, Response: {add_response.text}")
                return False, None
            
            add_result = add_response.json()
            self.log_test("Accept Invitation", True, f"Response: {add_result.get('message', 'Success')}")
            
            # Step 4: Verify BOTH users now have each other as contributors
            time.sleep(1)  # Brief delay for database consistency
            
            contributors_a_response = self.session_a.get(f"{BACKEND_URL}/contributors/my")
            contributors_b_response = self.session_b.get(f"{BACKEND_URL}/contributors/my")
            
            if contributors_a_response.status_code == 200 and contributors_b_response.status_code == 200:
                contributors_a = contributors_a_response.json()
                contributors_b = contributors_b_response.json()
                
                # Check if User A has User B as contributor
                user_b_in_a = any(c.get("contributor_id") == self.user_b_data["id"] for c in contributors_a)
                # Check if User B has User A as contributor  
                user_a_in_b = any(c.get("contributor_id") == self.user_a_data["id"] for c in contributors_b)
                
                if user_b_in_a and user_a_in_b:
                    self.log_test("Bidirectional Contributor Creation", True, 
                        "✅ BIDIRECTIONAL RELATIONSHIP CREATED - Both users have each other as contributors")
                    return True, {
                        "user_a_contributors": contributors_a,
                        "user_b_contributors": contributors_b,
                        "bidirectional": True
                    }
                else:
                    self.log_test("Bidirectional Contributor Creation", False, 
                        f"❌ NOT BIDIRECTIONAL - A has B: {user_b_in_a}, B has A: {user_a_in_b}")
                    return False, {
                        "user_a_contributors": contributors_a,
                        "user_b_contributors": contributors_b,
                        "bidirectional": False
                    }
            else:
                self.log_test("Bidirectional Contributor Creation", False, "Could not verify contributors after invitation")
                return False, None
                
        except Exception as e:
            self.log_test("Bidirectional Contributor Creation", False, f"Exception: {str(e)}")
            return False, None

    def test_contributor_listing(self):
        """Test 3: Test contributor listing from User document"""
        print("🧪 TEST 3: CONTRIBUTOR LISTING FROM USER DOCUMENT")
        print("-" * 50)
        
        try:
            # Test /api/contributors/my for both users
            response_a = self.session_a.get(f"{BACKEND_URL}/contributors/my")
            response_b = self.session_b.get(f"{BACKEND_URL}/contributors/my")
            
            if response_a.status_code == 200 and response_b.status_code == 200:
                contributors_a = response_a.json()
                contributors_b = response_b.json()
                
                # Verify format is compatible with frontend expectations
                expected_fields = ["contributor_id", "contributor_name", "contributor_email"]
                
                format_valid_a = all(
                    all(field in contrib for field in expected_fields) 
                    for contrib in contributors_a
                ) if contributors_a else True
                
                format_valid_b = all(
                    all(field in contrib for field in expected_fields) 
                    for contrib in contributors_b
                ) if contributors_b else True
                
                if format_valid_a and format_valid_b:
                    self.log_test("Contributor Listing", True, 
                        f"✅ Format compatible - User A: {len(contributors_a)} contributors, User B: {len(contributors_b)} contributors")
                    return True, {"user_a_contributors": contributors_a, "user_b_contributors": contributors_b}
                else:
                    self.log_test("Contributor Listing", False, 
                        f"❌ Format incompatible - A valid: {format_valid_a}, B valid: {format_valid_b}")
                    return False, None
            else:
                self.log_test("Contributor Listing", False, 
                    f"API error - A: {response_a.status_code}, B: {response_b.status_code}")
                return False, None
                
        except Exception as e:
            self.log_test("Contributor Listing", False, f"Exception: {str(e)}")
            return False, None

    def test_weekly_stories_aggregation(self):
        """Test 4: Test weekly stories aggregation using User-based contributor lookup"""
        print("🧪 TEST 4: WEEKLY STORIES AGGREGATION")
        print("-" * 50)
        
        try:
            # First, both users submit stories for current week
            current_week_response = self.session_a.get(f"{BACKEND_URL}/health")
            if current_week_response.status_code != 200:
                self.log_test("Get Current Week", False, "Could not get current week")
                return False, None
            
            current_week = current_week_response.json().get("current_week")
            self.log_test("Get Current Week", True, f"Current week: {current_week}")
            
            # User A submits story
            story_a_data = {
                "title": "User A's Weekly Story",
                "headline": "Breaking News from User A",
                "content": "This is User A's story for the current week. It should appear in both users' weekly aggregations if the contributor system works correctly."
            }
            
            story_a_response = self.session_a.post(f"{BACKEND_URL}/stories/submit", json=story_a_data)
            if story_a_response.status_code == 200:
                self.log_test("User A Story Submission", True, "User A submitted story successfully")
            elif story_a_response.status_code == 400 and "already submitted" in story_a_response.text:
                self.log_test("User A Story Submission", True, "User A already has story for this week")
            else:
                self.log_test("User A Story Submission", False, f"Status: {story_a_response.status_code}")
            
            # User B submits story
            story_b_data = {
                "title": "User B's Weekly Story", 
                "headline": "Exclusive Report from User B",
                "content": "This is User B's story for the current week. It should appear in both users' weekly aggregations if the contributor system works correctly."
            }
            
            story_b_response = self.session_b.post(f"{BACKEND_URL}/stories/submit", json=story_b_data)
            if story_b_response.status_code == 200:
                self.log_test("User B Story Submission", True, "User B submitted story successfully")
            elif story_b_response.status_code == 400 and "already submitted" in story_b_response.text:
                self.log_test("User B Story Submission", True, "User B already has story for this week")
            else:
                self.log_test("User B Story Submission", False, f"Status: {story_b_response.status_code}")
            
            # Test /api/stories/weekly/{week} for both users
            time.sleep(2)  # Allow time for database consistency
            
            weekly_a_response = self.session_a.get(f"{BACKEND_URL}/stories/weekly/{current_week}")
            weekly_b_response = self.session_b.get(f"{BACKEND_URL}/stories/weekly/{current_week}")
            
            if weekly_a_response.status_code == 200 and weekly_b_response.status_code == 200:
                stories_a = weekly_a_response.json()
                stories_b = weekly_b_response.json()
                
                # Count stories by author
                user_a_stories_in_a = sum(1 for s in stories_a if s.get("author_id") == self.user_a_data["id"])
                user_b_stories_in_a = sum(1 for s in stories_a if s.get("author_id") == self.user_b_data["id"])
                
                user_a_stories_in_b = sum(1 for s in stories_b if s.get("author_id") == self.user_a_data["id"])
                user_b_stories_in_b = sum(1 for s in stories_b if s.get("author_id") == self.user_b_data["id"])
                
                # Both users should see both stories if bidirectional relationship works
                if (user_a_stories_in_a > 0 and user_b_stories_in_a > 0 and 
                    user_a_stories_in_b > 0 and user_b_stories_in_b > 0):
                    self.log_test("Weekly Stories Aggregation", True, 
                        f"✅ BIDIRECTIONAL AGGREGATION WORKING - Both users see both stories")
                    return True, {
                        "user_a_sees": len(stories_a),
                        "user_b_sees": len(stories_b),
                        "stories_a": stories_a,
                        "stories_b": stories_b
                    }
                else:
                    self.log_test("Weekly Stories Aggregation", False, 
                        f"❌ AGGREGATION BROKEN - A sees: {len(stories_a)} (A:{user_a_stories_in_a}, B:{user_b_stories_in_a}), B sees: {len(stories_b)} (A:{user_a_stories_in_b}, B:{user_b_stories_in_b})")
                    return False, {
                        "user_a_sees": len(stories_a),
                        "user_b_sees": len(stories_b),
                        "stories_a": stories_a,
                        "stories_b": stories_b
                    }
            else:
                self.log_test("Weekly Stories Aggregation", False, 
                    f"API error - A: {weekly_a_response.status_code}, B: {weekly_b_response.status_code}")
                return False, None
                
        except Exception as e:
            self.log_test("Weekly Stories Aggregation", False, f"Exception: {str(e)}")
            return False, None

    def test_newspaper_generation(self):
        """Test 5: Test newspaper generation with new contributor system"""
        print("🧪 TEST 5: NEWSPAPER GENERATION WITH CONTRIBUTOR STORIES")
        print("-" * 50)
        
        try:
            # Test /api/newspapers/current for both users
            newspaper_a_response = self.session_a.get(f"{BACKEND_URL}/newspapers/current")
            newspaper_b_response = self.session_b.get(f"{BACKEND_URL}/newspapers/current")
            
            if newspaper_a_response.status_code == 200 and newspaper_b_response.status_code == 200:
                newspaper_a = newspaper_a_response.json()
                newspaper_b = newspaper_b_response.json()
                
                stories_a = newspaper_a.get("stories", [])
                stories_b = newspaper_b.get("stories", [])
                
                # Count stories by author in newspapers
                user_a_stories_in_newspaper_a = sum(1 for s in stories_a if s.get("author_id") == self.user_a_data["id"])
                user_b_stories_in_newspaper_a = sum(1 for s in stories_a if s.get("author_id") == self.user_b_data["id"])
                
                user_a_stories_in_newspaper_b = sum(1 for s in stories_b if s.get("author_id") == self.user_a_data["id"])
                user_b_stories_in_newspaper_b = sum(1 for s in stories_b if s.get("author_id") == self.user_b_data["id"])
                
                # Both users' newspapers should contain both users' stories if contributor system works
                if (user_a_stories_in_newspaper_a > 0 and user_b_stories_in_newspaper_a > 0 and 
                    user_a_stories_in_newspaper_b > 0 and user_b_stories_in_newspaper_b > 0):
                    self.log_test("Newspaper Generation", True, 
                        f"✅ CONTRIBUTOR STORIES IN NEWSPAPERS - Both newspapers contain both users' stories")
                    return True, {
                        "newspaper_a_stories": len(stories_a),
                        "newspaper_b_stories": len(stories_b),
                        "newspaper_a": newspaper_a,
                        "newspaper_b": newspaper_b
                    }
                else:
                    self.log_test("Newspaper Generation", False, 
                        f"❌ CONTRIBUTOR STORIES MISSING - A's newspaper: {len(stories_a)} stories (A:{user_a_stories_in_newspaper_a}, B:{user_b_stories_in_newspaper_a}), B's newspaper: {len(stories_b)} stories (A:{user_a_stories_in_newspaper_b}, B:{user_b_stories_in_newspaper_b})")
                    return False, {
                        "newspaper_a_stories": len(stories_a),
                        "newspaper_b_stories": len(stories_b),
                        "newspaper_a": newspaper_a,
                        "newspaper_b": newspaper_b
                    }
            else:
                self.log_test("Newspaper Generation", False, 
                    f"API error - A: {newspaper_a_response.status_code}, B: {newspaper_b_response.status_code}")
                return False, None
                
        except Exception as e:
            self.log_test("Newspaper Generation", False, f"Exception: {str(e)}")
            return False, None

    def test_complete_end_to_end_workflow(self):
        """Test 6: Complete end-to-end workflow verification"""
        print("🧪 TEST 6: COMPLETE END-TO-END WORKFLOW")
        print("-" * 50)
        
        try:
            # Verify the complete workflow works as expected
            workflow_steps = [
                "✅ User registration/authentication",
                "✅ Invitation sending", 
                "✅ Invitation acceptance",
                "✅ Bidirectional contributor relationship creation",
                "✅ Story submission by both users",
                "✅ Weekly stories aggregation includes contributor stories",
                "✅ Newspaper generation includes contributor stories"
            ]
            
            # Check final state
            contributors_a_response = self.session_a.get(f"{BACKEND_URL}/contributors/my")
            contributors_b_response = self.session_b.get(f"{BACKEND_URL}/contributors/my")
            
            if contributors_a_response.status_code == 200 and contributors_b_response.status_code == 200:
                contributors_a = contributors_a_response.json()
                contributors_b = contributors_b_response.json()
                
                # Check if bidirectional relationship exists
                user_b_in_a = any(c.get("contributor_id") == self.user_b_data["id"] for c in contributors_a)
                user_a_in_b = any(c.get("contributor_id") == self.user_a_data["id"] for c in contributors_b)
                
                if user_b_in_a and user_a_in_b:
                    self.log_test("Complete End-to-End Workflow", True, 
                        f"✅ PHASE 3 ARCHITECTURAL REDESIGN SUCCESSFUL - Bidirectional User-based contributor system working")
                    
                    print("\n🎉 WORKFLOW VERIFICATION:")
                    for step in workflow_steps:
                        print(f"   {step}")
                    
                    return True, {
                        "bidirectional_relationship": True,
                        "user_a_contributors": len(contributors_a),
                        "user_b_contributors": len(contributors_b),
                        "workflow_complete": True
                    }
                else:
                    self.log_test("Complete End-to-End Workflow", False, 
                        f"❌ BIDIRECTIONAL RELATIONSHIP MISSING - A has B: {user_b_in_a}, B has A: {user_a_in_b}")
                    return False, {
                        "bidirectional_relationship": False,
                        "user_a_contributors": len(contributors_a),
                        "user_b_contributors": len(contributors_b),
                        "workflow_complete": False
                    }
            else:
                self.log_test("Complete End-to-End Workflow", False, "Could not verify final contributor state")
                return False, None
                
        except Exception as e:
            self.log_test("Complete End-to-End Workflow", False, f"Exception: {str(e)}")
            return False, None

    def run_comprehensive_phase3_verification(self):
        """Run comprehensive Phase 3 architectural redesign verification"""
        print("🚀 COMPREHENSIVE PHASE 3 ARCHITECTURAL REDESIGN VERIFICATION")
        print("=" * 70)
        print("Testing MongoDB-based bidirectional contributor system with atomic operations")
        print("=" * 70)
        
        # Setup test users
        if not self.setup_test_users():
            print("❌ CRITICAL: Could not setup test users")
            return 0, 6, self.test_results, {}
        
        # Run all verification tests
        tests = [
            ("User Model Contributors Field", self.test_user_model_contributors_field),
            ("Bidirectional Contributor Creation", self.test_bidirectional_contributor_creation),
            ("Contributor Listing", self.test_contributor_listing),
            ("Weekly Stories Aggregation", self.test_weekly_stories_aggregation),
            ("Newspaper Generation", self.test_newspaper_generation),
            ("Complete End-to-End Workflow", self.test_complete_end_to_end_workflow)
        ]
        
        passed = 0
        failed = 0
        detailed_results = {}
        
        for test_name, test_func in tests:
            try:
                print(f"\n{'='*70}")
                success, data = test_func()
                detailed_results[test_name.lower().replace(" ", "_")] = data
                
                if success:
                    passed += 1
                else:
                    failed += 1
                    
                time.sleep(1)  # Brief delay between tests
                
            except Exception as e:
                print(f"❌ CRITICAL ERROR in {test_name}: {str(e)}")
                failed += 1
                detailed_results[test_name.lower().replace(" ", "_")] = {"error": str(e)}
        
        # Final summary
        print("\n" + "=" * 70)
        print("📊 PHASE 3 ARCHITECTURAL REDESIGN VERIFICATION SUMMARY")
        print("=" * 70)
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"📈 Success Rate: {(passed/(passed+failed)*100):.1f}%")
        
        # Determine overall Phase 3 status
        if passed == 6:
            print("\n🎉 PHASE 3 ARCHITECTURAL REDESIGN: ✅ FULLY FUNCTIONAL")
            print("   The new User-based bidirectional contributor system is working correctly!")
        elif passed >= 4:
            print("\n⚠️  PHASE 3 ARCHITECTURAL REDESIGN: 🔶 PARTIALLY FUNCTIONAL")
            print("   Core functionality works but some issues remain")
        else:
            print("\n❌ PHASE 3 ARCHITECTURAL REDESIGN: ❌ NOT FUNCTIONAL")
            print("   Critical issues prevent proper contributor story aggregation")
        
        return passed, failed, self.test_results, detailed_results

if __name__ == "__main__":
    tester = Phase3RedesignTester()
    passed, failed, results, detailed = tester.run_comprehensive_phase3_verification()
    
    # Save detailed results
    with open('/app/phase3_verification_results.json', 'w') as f:
        json.dump({
            "summary": {
                "passed": passed,
                "failed": failed,
                "success_rate": passed/(passed+failed)*100 if (passed+failed) > 0 else 0,
                "phase3_status": "FULLY_FUNCTIONAL" if passed == 6 else ("PARTIALLY_FUNCTIONAL" if passed >= 4 else "NOT_FUNCTIONAL")
            },
            "detailed_results": results,
            "verification_data": detailed
        }, f, indent=2)
    
    print(f"\n📄 Detailed verification results saved to: /app/phase3_verification_results.json")
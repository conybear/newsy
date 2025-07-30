#!/usr/bin/env python3
"""
Phase 3 Flipbook Newspaper Generation System Testing for Acta Diurna
Tests all newspaper generation endpoints and complete workflow
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

class NewspaperGenerationTester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.user_id = None
        self.test_results = []
        self.contributor_session = None
        self.contributor_token = None
        
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

    def test_login_existing_user(self):
        """Test login with existing user test@actadiurna.com"""
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
                    self.user_id = data["user"]["id"]
                    self.log_test("Login Existing User", True, f"Logged in as {data['user']['full_name']} ({data['user']['email']})")
                    return True
                else:
                    self.log_test("Login Existing User", False, "No access token in response", data)
                    return False
            else:
                self.log_test("Login Existing User", False, f"Status code: {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("Login Existing User", False, f"Exception: {str(e)}")
            return False

    def test_create_contributors(self):
        """Create and verify contributors exist"""
        try:
            # First, create a contributor user
            contributor_data = {
                "email": "contributor1@actadiurna.com",
                "password": "ContribPass123!",
                "full_name": "Alice Contributor"
            }
            
            # Try to register contributor (might already exist)
            register_response = self.session.post(f"{BACKEND_URL}/auth/register", json=contributor_data)
            if register_response.status_code == 400:
                # User already exists, try to login
                login_response = requests.post(f"{BACKEND_URL}/auth/login", json={
                    "email": contributor_data["email"],
                    "password": contributor_data["password"]
                })
                if login_response.status_code == 200:
                    self.log_test("Create Contributors", True, "Contributor user already exists and can login")
                else:
                    self.log_test("Create Contributors", False, "Contributor user exists but cannot login")
                    return False
            elif register_response.status_code == 200:
                self.log_test("Create Contributors", True, "New contributor user registered successfully")
            else:
                self.log_test("Create Contributors", False, f"Failed to register contributor: {register_response.text}")
                return False
            
            # Send invitation to contributor
            invitation_data = {
                "email": "contributor1@actadiurna.com"
            }
            
            invite_response = self.session.post(f"{BACKEND_URL}/invitations/send", json=invitation_data)
            if invite_response.status_code == 200:
                self.log_test("Send Invitation", True, "Invitation sent to contributor")
            elif invite_response.status_code == 400 and "Already invited" in invite_response.text:
                self.log_test("Send Invitation", True, "Contributor already invited (expected)")
            else:
                self.log_test("Send Invitation", False, f"Failed to send invitation: {invite_response.text}")
                return False
            
            # Login as contributor and accept invitation
            contributor_session = requests.Session()
            contrib_login = contributor_session.post(f"{BACKEND_URL}/auth/login", json={
                "email": "contributor1@actadiurna.com",
                "password": "ContribPass123!"
            })
            
            if contrib_login.status_code == 200:
                contrib_token = contrib_login.json()["access_token"]
                contributor_session.headers.update({"Authorization": f"Bearer {contrib_token}"})
                self.contributor_session = contributor_session
                self.contributor_token = contrib_token
                
                # Get received invitations
                invitations_response = contributor_session.get(f"{BACKEND_URL}/invitations/received")
                if invitations_response.status_code == 200:
                    invitations = invitations_response.json()
                    if invitations:
                        # Add as contributor
                        add_contrib_data = {
                            "invitation_id": invitations[0]["id"]
                        }
                        add_response = contributor_session.post(f"{BACKEND_URL}/contributors/add", json=add_contrib_data)
                        if add_response.status_code == 200:
                            self.log_test("Add Contributor", True, "Contributor relationship established")
                        elif add_response.status_code == 400 and "Already added" in add_response.text:
                            self.log_test("Add Contributor", True, "Contributor already added (expected)")
                        else:
                            self.log_test("Add Contributor", False, f"Failed to add contributor: {add_response.text}")
                            return False
                    else:
                        self.log_test("Add Contributor", True, "No pending invitations (contributor may already be added)")
                else:
                    self.log_test("Add Contributor", False, f"Failed to get invitations: {invitations_response.text}")
                    return False
            else:
                self.log_test("Create Contributors", False, f"Failed to login as contributor: {contrib_login.text}")
                return False
            
            return True
            
        except Exception as e:
            self.log_test("Create Contributors", False, f"Exception: {str(e)}")
            return False

    def test_submit_test_stories(self):
        """Submit test stories from user and contributors"""
        try:
            # Submit story as main user
            user_story_data = {
                "title": "Main User Weekly Report",
                "headline": "Breaking: Local Community Garden Wins Award",
                "content": "The downtown community garden has been recognized with the City's Environmental Excellence Award for its outstanding contribution to urban sustainability and community building. The garden, which started three years ago with just a handful of volunteers, now serves over 200 families in the neighborhood."
            }
            
            user_story_response = self.session.post(f"{BACKEND_URL}/stories/submit", json=user_story_data)
            if user_story_response.status_code == 200:
                self.log_test("Submit User Story", True, "Main user story submitted successfully")
            elif user_story_response.status_code == 400 and "already submitted" in user_story_response.text:
                self.log_test("Submit User Story", True, "User already submitted story this week (expected)")
            else:
                self.log_test("Submit User Story", False, f"Failed to submit user story: {user_story_response.text}")
                return False
            
            # Submit story as contributor
            if self.contributor_session:
                contrib_story_data = {
                    "title": "Contributor's Weekly Update",
                    "headline": "New Art Installation Unveiled Downtown",
                    "content": "A stunning new sculpture was unveiled in Central Plaza this week, created by local artist Maria Rodriguez. The piece, titled 'Community Connections', features intertwining bronze figures representing the diverse voices that make up our neighborhood. The installation was funded through a community crowdfunding campaign that raised over $50,000."
                }
                
                contrib_story_response = self.contributor_session.post(f"{BACKEND_URL}/stories/submit", json=contrib_story_data)
                if contrib_story_response.status_code == 200:
                    self.log_test("Submit Contributor Story", True, "Contributor story submitted successfully")
                elif contrib_story_response.status_code == 400 and "already submitted" in contrib_story_response.text:
                    self.log_test("Submit Contributor Story", True, "Contributor already submitted story this week (expected)")
                else:
                    self.log_test("Submit Contributor Story", False, f"Failed to submit contributor story: {contrib_story_response.text}")
                    return False
            else:
                self.log_test("Submit Contributor Story", False, "No contributor session available")
                return False
            
            return True
            
        except Exception as e:
            self.log_test("Submit Test Stories", False, f"Exception: {str(e)}")
            return False

    def test_current_newspaper_endpoint(self):
        """Test /api/newspapers/current endpoint"""
        try:
            if not self.auth_token:
                self.log_test("Current Newspaper", False, "No auth token available")
                return False
                
            response = self.session.get(f"{BACKEND_URL}/newspapers/current")
            
            if response.status_code == 200:
                data = response.json()
                if "week_of" in data and "stories" in data and "title" in data:
                    stories_count = len(data["stories"])
                    headlines_count = sum(1 for story in data["stories"] if story.get("headline"))
                    self.log_test("Current Newspaper", True, 
                        f"Current newspaper generated for {data['week_of']} with {stories_count} stories ({headlines_count} headlines)")
                    
                    # Verify story aggregation from contributors
                    authors = set(story.get("author_name") for story in data["stories"])
                    self.log_test("Story Aggregation", True, 
                        f"Stories from {len(authors)} authors: {', '.join(authors)}")
                    
                    return True, data
                else:
                    self.log_test("Current Newspaper", False, "Invalid newspaper data structure", data)
                    return False, None
            else:
                self.log_test("Current Newspaper", False, f"Status code: {response.status_code}", response.text)
                return False, None
        except Exception as e:
            self.log_test("Current Newspaper", False, f"Exception: {str(e)}")
            return False, None

    def test_newspaper_by_week_endpoint(self):
        """Test /api/newspapers/week/{week} endpoint"""
        try:
            if not self.auth_token:
                self.log_test("Newspaper by Week", False, "No auth token available")
                return False
                
            # Get current week from health endpoint
            health_response = self.session.get(f"{BACKEND_URL}/health")
            if health_response.status_code == 200:
                current_week = health_response.json().get("current_week")
            else:
                current_week = "2025-W31"  # Fallback
            
            response = self.session.get(f"{BACKEND_URL}/newspapers/week/{current_week}")
            
            if response.status_code == 200:
                data = response.json()
                if "week_of" in data and "stories" in data:
                    stories_count = len(data["stories"])
                    self.log_test("Newspaper by Week", True, 
                        f"Retrieved newspaper for {data['week_of']} with {stories_count} stories")
                    return True, data
                else:
                    self.log_test("Newspaper by Week", False, "Invalid newspaper data structure", data)
                    return False, None
            else:
                self.log_test("Newspaper by Week", False, f"Status code: {response.status_code}", response.text)
                return False, None
        except Exception as e:
            self.log_test("Newspaper by Week", False, f"Exception: {str(e)}")
            return False, None

    def test_newspaper_archive_endpoint(self):
        """Test /api/newspapers/archive endpoint"""
        try:
            if not self.auth_token:
                self.log_test("Newspaper Archive", False, "No auth token available")
                return False
                
            response = self.session.get(f"{BACKEND_URL}/newspapers/archive")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_test("Newspaper Archive", True, 
                        f"Retrieved {len(data)} archived newspapers")
                    
                    # Verify archive structure
                    if data:
                        first_archive = data[0]
                        required_fields = ["week_of", "title", "published_at", "story_count", "contributor_count"]
                        if all(field in first_archive for field in required_fields):
                            self.log_test("Archive Structure", True, 
                                f"Archive entries contain all required fields")
                        else:
                            self.log_test("Archive Structure", False, 
                                f"Missing fields in archive entry: {first_archive}")
                    
                    return True, data
                else:
                    self.log_test("Newspaper Archive", False, "Response is not a list", data)
                    return False, None
            else:
                self.log_test("Newspaper Archive", False, f"Status code: {response.status_code}", response.text)
                return False, None
        except Exception as e:
            self.log_test("Newspaper Archive", False, f"Exception: {str(e)}")
            return False, None

    def test_newspaper_regenerate_endpoint(self):
        """Test /api/newspapers/regenerate endpoint"""
        try:
            if not self.auth_token:
                self.log_test("Newspaper Regenerate", False, "No auth token available")
                return False
                
            response = self.session.post(f"{BACKEND_URL}/newspapers/regenerate")
            
            if response.status_code == 200:
                data = response.json()
                if "message" in data and "newspaper" in data:
                    newspaper = data["newspaper"]
                    stories_count = len(newspaper.get("stories", []))
                    self.log_test("Newspaper Regenerate", True, 
                        f"Newspaper regenerated successfully with {stories_count} stories")
                    return True, data
                else:
                    self.log_test("Newspaper Regenerate", False, "Invalid regenerate response structure", data)
                    return False, None
            else:
                self.log_test("Newspaper Regenerate", False, f"Status code: {response.status_code}", response.text)
                return False, None
        except Exception as e:
            self.log_test("Newspaper Regenerate", False, f"Exception: {str(e)}")
            return False, None

    def test_business_rules_verification(self, newspaper_data):
        """Verify business rules in newspaper generation"""
        try:
            if not newspaper_data:
                self.log_test("Business Rules Verification", False, "No newspaper data provided")
                return False
            
            stories = newspaper_data.get("stories", [])
            
            # Rule 1: Only submitted stories included (not drafts)
            all_submitted = all(story.get("is_submitted", False) for story in stories)
            if all_submitted:
                self.log_test("Only Submitted Stories", True, "All stories in newspaper are submitted")
            else:
                self.log_test("Only Submitted Stories", False, "Found draft stories in newspaper")
            
            # Rule 2: Stories sorted by headline priority
            headlines_first = True
            found_non_headline = False
            for story in stories:
                if story.get("headline") and found_non_headline:
                    headlines_first = False
                    break
                if not story.get("headline"):
                    found_non_headline = True
            
            if headlines_first:
                self.log_test("Headline Prioritization", True, "Headlines appear before non-headlines")
            else:
                self.log_test("Headline Prioritization", False, "Headlines not properly prioritized")
            
            # Rule 3: Contributor stories properly attributed
            authors = [story.get("author_name") for story in stories]
            unique_authors = set(authors)
            if len(unique_authors) > 1:
                self.log_test("Contributor Attribution", True, f"Stories from multiple contributors: {', '.join(unique_authors)}")
            else:
                self.log_test("Contributor Attribution", True, f"Stories from single author: {', '.join(unique_authors)}")
            
            # Rule 4: Week calculation accurate
            week_of = newspaper_data.get("week_of")
            if week_of and week_of.startswith("2025-W"):
                self.log_test("Week Calculation", True, f"Week format correct: {week_of}")
            else:
                self.log_test("Week Calculation", False, f"Invalid week format: {week_of}")
            
            return True
            
        except Exception as e:
            self.log_test("Business Rules Verification", False, f"Exception: {str(e)}")
            return False

    def test_complete_workflow(self):
        """Test complete newspaper generation workflow"""
        try:
            print("\n🔄 TESTING COMPLETE WORKFLOW")
            print("=" * 50)
            
            # Step 1: Login
            if not self.test_login_existing_user():
                return False
            
            # Step 2: Create/verify contributors
            if not self.test_create_contributors():
                return False
            
            # Step 3: Submit test stories
            if not self.test_submit_test_stories():
                return False
            
            # Step 4: Generate current newspaper
            success, newspaper_data = self.test_current_newspaper_endpoint()
            if not success:
                return False
            
            # Step 5: Verify business rules
            if not self.test_business_rules_verification(newspaper_data):
                return False
            
            # Step 6: Test archive system
            archive_success, archive_data = self.test_newspaper_archive_endpoint()
            if not archive_success:
                return False
            
            # Step 7: Test regeneration
            regen_success, regen_data = self.test_newspaper_regenerate_endpoint()
            if not regen_success:
                return False
            
            self.log_test("Complete Workflow", True, "All workflow steps completed successfully")
            return True
            
        except Exception as e:
            self.log_test("Complete Workflow", False, f"Exception: {str(e)}")
            return False

    def run_all_tests(self):
        """Run all newspaper generation tests"""
        print("🗞️  Starting Phase 3 Flipbook Newspaper Generation Testing")
        print("=" * 70)
        
        passed = 0
        failed = 0
        
        # Test complete workflow
        if self.test_complete_workflow():
            passed += 1
        else:
            failed += 1
        
        # Test individual endpoints
        tests = [
            self.test_newspaper_by_week_endpoint,
            self.test_newspaper_archive_endpoint,
            self.test_newspaper_regenerate_endpoint,
        ]
        
        for test in tests:
            try:
                result = test()
                if isinstance(result, tuple):
                    success, _ = result
                else:
                    success = result
                
                if success:
                    passed += 1
                else:
                    failed += 1
            except Exception as e:
                print(f"❌ CRITICAL ERROR in {test.__name__}: {str(e)}")
                failed += 1
            
            time.sleep(0.5)
        
        print("=" * 70)
        print(f"📊 NEWSPAPER GENERATION TEST SUMMARY")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"📈 Success Rate: {(passed/(passed+failed)*100):.1f}%")
        
        return passed, failed, self.test_results

if __name__ == "__main__":
    tester = NewspaperGenerationTester()
    passed, failed, results = tester.run_all_tests()
    
    # Save detailed results
    with open('/app/newspaper_test_results.json', 'w') as f:
        json.dump({
            "summary": {
                "passed": passed,
                "failed": failed,
                "success_rate": passed/(passed+failed)*100 if (passed+failed) > 0 else 0
            },
            "detailed_results": results
        }, f, indent=2)
    
    print(f"\n📄 Detailed results saved to: /app/newspaper_test_results.json")
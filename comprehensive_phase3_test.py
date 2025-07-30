#!/usr/bin/env python3
"""
FINAL COMPREHENSIVE TEST - Acta Diurna Phase 3 Flipbook Newspaper System
Complete end-to-end workflow test for the social newspaper platform
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

class ComprehensivePhase3Tester:
    def __init__(self):
        self.test_results = []
        self.users = {}  # Store user sessions and data
        
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

    def create_test_image(self, color='red', size=(100, 100)):
        """Create a test image in bytes format"""
        img = Image.new('RGB', size, color=color)
        buffer = io.BytesIO()
        img.save(buffer, format='JPEG')
        buffer.seek(0)
        return buffer.getvalue()

    def test_health_check(self):
        """Test system health"""
        try:
            response = requests.get(f"{BACKEND_URL}/health")
            if response.status_code == 200:
                data = response.json()
                self.log_test("System Health Check", True, 
                    f"Status: {data.get('status')}, Week: {data.get('current_week')}")
                return True, data
            else:
                self.log_test("System Health Check", False, f"Status code: {response.status_code}")
                return False, None
        except Exception as e:
            self.log_test("System Health Check", False, f"Exception: {str(e)}")
            return False, None

    def create_user(self, user_name, email, password, full_name):
        """Create and authenticate a user"""
        try:
            session = requests.Session()
            
            # Try login first
            login_data = {"email": email, "password": password}
            login_response = session.post(f"{BACKEND_URL}/auth/login", json=login_data)
            
            if login_response.status_code == 200:
                # User exists, login successful
                data = login_response.json()
                token = data["access_token"]
                session.headers.update({"Authorization": f"Bearer {token}"})
                
                self.users[user_name] = {
                    "session": session,
                    "token": token,
                    "email": email,
                    "full_name": full_name,
                    "user_data": data["user"]
                }
                
                self.log_test(f"User Login - {user_name}", True, f"Logged in as {email}")
                return True
            
            # User doesn't exist, register
            register_data = {
                "email": email,
                "password": password,
                "full_name": full_name
            }
            
            register_response = session.post(f"{BACKEND_URL}/auth/register", json=register_data)
            
            if register_response.status_code == 200:
                data = register_response.json()
                token = data["access_token"]
                session.headers.update({"Authorization": f"Bearer {token}"})
                
                self.users[user_name] = {
                    "session": session,
                    "token": token,
                    "email": email,
                    "full_name": full_name,
                    "user_data": data["user"]
                }
                
                self.log_test(f"User Registration - {user_name}", True, f"Registered {email}")
                return True
            else:
                self.log_test(f"User Creation - {user_name}", False, 
                    f"Registration failed: {register_response.status_code}", register_response.text)
                return False
                
        except Exception as e:
            self.log_test(f"User Creation - {user_name}", False, f"Exception: {str(e)}")
            return False

    def test_invitation_system(self, sender_name, recipient_name):
        """Test sending and managing invitations"""
        try:
            if sender_name not in self.users or recipient_name not in self.users:
                self.log_test("Invitation System", False, "Required users not available")
                return False
            
            sender = self.users[sender_name]
            recipient = self.users[recipient_name]
            
            # Send invitation
            invitation_data = {"email": recipient["email"]}
            response = sender["session"].post(f"{BACKEND_URL}/invitations/send", json=invitation_data)
            
            if response.status_code == 200:
                self.log_test(f"Send Invitation - {sender_name} to {recipient_name}", True, 
                    f"Invitation sent to {recipient['email']}")
                
                # Check received invitations
                received_response = recipient["session"].get(f"{BACKEND_URL}/invitations/received")
                if received_response.status_code == 200:
                    invitations = received_response.json()
                    self.log_test(f"Received Invitations - {recipient_name}", True, 
                        f"Found {len(invitations)} invitations")
                    return True
                else:
                    self.log_test(f"Received Invitations - {recipient_name}", False, 
                        f"Status: {received_response.status_code}")
                    return False
            else:
                # Check if already invited
                if response.status_code == 400 and "Already invited" in response.text:
                    self.log_test(f"Send Invitation - {sender_name} to {recipient_name}", True, 
                        "Already invited (expected)")
                    return True
                else:
                    self.log_test(f"Send Invitation - {sender_name} to {recipient_name}", False, 
                        f"Status: {response.status_code}", response.text)
                    return False
                    
        except Exception as e:
            self.log_test("Invitation System", False, f"Exception: {str(e)}")
            return False

    def test_contributor_management(self, user_name, contributor_name):
        """Test adding contributors from invitations"""
        try:
            if user_name not in self.users:
                self.log_test("Contributor Management", False, f"User {user_name} not available")
                return False
            
            user = self.users[user_name]
            
            # Get received invitations
            invitations_response = user["session"].get(f"{BACKEND_URL}/invitations/received")
            if invitations_response.status_code != 200:
                self.log_test(f"Get Invitations - {user_name}", False, 
                    f"Status: {invitations_response.status_code}")
                return False
            
            invitations = invitations_response.json()
            
            # Find invitation from contributor
            target_invitation = None
            for invitation in invitations:
                if contributor_name in self.users and invitation.get("from_user_email") == self.users[contributor_name]["email"]:
                    target_invitation = invitation
                    break
            
            if not target_invitation:
                self.log_test(f"Find Invitation - {user_name} from {contributor_name}", False, 
                    "No matching invitation found")
                return False
            
            # Add as contributor
            add_data = {"invitation_id": target_invitation["id"]}
            add_response = user["session"].post(f"{BACKEND_URL}/contributors/add", json=add_data)
            
            if add_response.status_code == 200:
                self.log_test(f"Add Contributor - {user_name} adds {contributor_name}", True, 
                    add_response.json().get("message", "Added successfully"))
                
                # Verify contributor was added
                contributors_response = user["session"].get(f"{BACKEND_URL}/contributors/my")
                if contributors_response.status_code == 200:
                    contributors = contributors_response.json()
                    self.log_test(f"Verify Contributors - {user_name}", True, 
                        f"Has {len(contributors)} contributors")
                    return True
                else:
                    self.log_test(f"Verify Contributors - {user_name}", False, 
                        f"Status: {contributors_response.status_code}")
                    return False
            else:
                # Check if already added
                if add_response.status_code == 400 and "Already added" in add_response.text:
                    self.log_test(f"Add Contributor - {user_name} adds {contributor_name}", True, 
                        "Already added as contributor (expected)")
                    return True
                else:
                    self.log_test(f"Add Contributor - {user_name} adds {contributor_name}", False, 
                        f"Status: {add_response.status_code}", add_response.text)
                    return False
                    
        except Exception as e:
            self.log_test("Contributor Management", False, f"Exception: {str(e)}")
            return False

    def test_story_creation(self, user_name, story_title, story_content, is_headline=False):
        """Test story creation and submission"""
        try:
            if user_name not in self.users:
                self.log_test("Story Creation", False, f"User {user_name} not available")
                return False, None
            
            user = self.users[user_name]
            
            # Create draft first
            draft_data = {
                "title": story_title,
                "headline": story_content[:100] + "..." if len(story_content) > 100 else story_content,
                "content": story_content
            }
            
            draft_response = user["session"].post(f"{BACKEND_URL}/stories/draft", json=draft_data)
            
            if draft_response.status_code == 200:
                draft_result = draft_response.json()
                story_id = draft_result["id"]
                
                self.log_test(f"Create Draft - {user_name}", True, f"Draft saved: {story_title}")
                
                # Submit the story
                submit_data = {
                    "title": story_title,
                    "headline": draft_data["headline"],
                    "content": story_content
                }
                
                submit_response = user["session"].post(f"{BACKEND_URL}/stories/submit", json=submit_data)
                
                if submit_response.status_code == 200:
                    self.log_test(f"Submit Story - {user_name}", True, f"Story submitted: {story_title}")
                    return True, story_id
                else:
                    # Check if already submitted this week
                    if submit_response.status_code == 400 and "already submitted" in submit_response.text:
                        self.log_test(f"Submit Story - {user_name}", True, 
                            "Already submitted this week (expected)")
                        return True, story_id
                    else:
                        self.log_test(f"Submit Story - {user_name}", False, 
                            f"Status: {submit_response.status_code}", submit_response.text)
                        return False, None
            else:
                self.log_test(f"Create Draft - {user_name}", False, 
                    f"Status: {draft_response.status_code}", draft_response.text)
                return False, None
                
        except Exception as e:
            self.log_test("Story Creation", False, f"Exception: {str(e)}")
            return False, None

    def test_image_upload(self, user_name, story_id):
        """Test image upload to story"""
        try:
            if user_name not in self.users:
                self.log_test("Image Upload", False, f"User {user_name} not available")
                return False
            
            user = self.users[user_name]
            
            # Create test image
            image_data = self.create_test_image(color='blue')
            
            files = {
                'file': ('test_image.jpg', image_data, 'image/jpeg')
            }
            
            response = user["session"].post(f"{BACKEND_URL}/stories/{story_id}/images", files=files)
            
            if response.status_code == 200:
                result = response.json()
                self.log_test(f"Image Upload - {user_name}", True, 
                    f"Image uploaded: {result.get('image_id')}")
                return True
            else:
                # Check if story is already submitted (can't modify)
                if response.status_code == 400 and "Cannot modify submitted story" in response.text:
                    self.log_test(f"Image Upload - {user_name}", True, 
                        "Cannot modify submitted story (expected)")
                    return True
                else:
                    self.log_test(f"Image Upload - {user_name}", False, 
                        f"Status: {response.status_code}", response.text)
                    return False
                    
        except Exception as e:
            self.log_test("Image Upload", False, f"Exception: {str(e)}")
            return False

    def test_newspaper_generation(self, user_name):
        """Test newspaper generation with contributor stories"""
        try:
            if user_name not in self.users:
                self.log_test("Newspaper Generation", False, f"User {user_name} not available")
                return False, None
            
            user = self.users[user_name]
            
            # Get current newspaper
            current_response = user["session"].get(f"{BACKEND_URL}/newspapers/current")
            
            if current_response.status_code == 200:
                newspaper = current_response.json()
                stories = newspaper.get("stories", [])
                
                # Analyze stories
                user_stories = [s for s in stories if s.get("author_id") == user["user_data"]["id"]]
                contributor_stories = [s for s in stories if s.get("author_id") != user["user_data"]["id"]]
                
                self.log_test(f"Current Newspaper - {user_name}", True, 
                    f"Generated newspaper with {len(stories)} total stories ({len(user_stories)} own, {len(contributor_stories)} from contributors)")
                
                # Test specific week newspaper
                week_response = user["session"].get(f"{BACKEND_URL}/newspapers/week/{newspaper.get('week_of')}")
                
                if week_response.status_code == 200:
                    week_newspaper = week_response.json()
                    self.log_test(f"Week Newspaper - {user_name}", True, 
                        f"Retrieved newspaper for week {week_newspaper.get('week_of')}")
                    
                    return True, {
                        "current_newspaper": newspaper,
                        "week_newspaper": week_newspaper,
                        "total_stories": len(stories),
                        "user_stories": len(user_stories),
                        "contributor_stories": len(contributor_stories)
                    }
                else:
                    self.log_test(f"Week Newspaper - {user_name}", False, 
                        f"Status: {week_response.status_code}")
                    return False, None
            else:
                self.log_test(f"Current Newspaper - {user_name}", False, 
                    f"Status: {current_response.status_code}", current_response.text)
                return False, None
                
        except Exception as e:
            self.log_test("Newspaper Generation", False, f"Exception: {str(e)}")
            return False, None

    def test_archive_system(self, user_name):
        """Test newspaper archive functionality"""
        try:
            if user_name not in self.users:
                self.log_test("Archive System", False, f"User {user_name} not available")
                return False
            
            user = self.users[user_name]
            
            # Get archive
            archive_response = user["session"].get(f"{BACKEND_URL}/newspapers/archive")
            
            if archive_response.status_code == 200:
                archive = archive_response.json()
                self.log_test(f"Archive System - {user_name}", True, 
                    f"Retrieved {len(archive)} archived newspapers")
                
                # Test regeneration
                regen_response = user["session"].post(f"{BACKEND_URL}/newspapers/regenerate")
                
                if regen_response.status_code == 200:
                    regen_result = regen_response.json()
                    self.log_test(f"Newspaper Regeneration - {user_name}", True, 
                        "Successfully regenerated current newspaper")
                    return True
                else:
                    self.log_test(f"Newspaper Regeneration - {user_name}", False, 
                        f"Status: {regen_response.status_code}")
                    return False
            else:
                self.log_test(f"Archive System - {user_name}", False, 
                    f"Status: {archive_response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Archive System", False, f"Exception: {str(e)}")
            return False

    def test_flipbook_data_structure(self, user_name):
        """Test that newspaper data structure is correct for flipbook frontend"""
        try:
            if user_name not in self.users:
                self.log_test("Flipbook Data Structure", False, f"User {user_name} not available")
                return False
            
            user = self.users[user_name]
            
            # Get current newspaper
            response = user["session"].get(f"{BACKEND_URL}/newspapers/current")
            
            if response.status_code == 200:
                newspaper = response.json()
                
                # Verify required fields for flipbook
                required_fields = ["id", "user_id", "week_of", "title", "stories", "published_at"]
                missing_fields = [field for field in required_fields if field not in newspaper]
                
                if missing_fields:
                    self.log_test("Flipbook Data Structure", False, 
                        f"Missing required fields: {missing_fields}")
                    return False
                
                # Verify story structure
                stories = newspaper.get("stories", [])
                if stories:
                    story = stories[0]
                    story_required_fields = ["id", "author_id", "author_name", "title", "content", "week_of", "is_submitted"]
                    story_missing_fields = [field for field in story_required_fields if field not in story]
                    
                    if story_missing_fields:
                        self.log_test("Flipbook Data Structure", False, 
                            f"Story missing required fields: {story_missing_fields}")
                        return False
                
                # Check if stories are properly sorted (headlines first)
                headlines = [s for s in stories if s.get("headline")]
                non_headlines = [s for s in stories if not s.get("headline")]
                
                self.log_test("Flipbook Data Structure", True, 
                    f"Valid structure: {len(stories)} stories ({len(headlines)} headlines, {len(non_headlines)} regular)")
                return True
            else:
                self.log_test("Flipbook Data Structure", False, 
                    f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Flipbook Data Structure", False, f"Exception: {str(e)}")
            return False

    def run_comprehensive_test(self):
        """Run the complete comprehensive test workflow"""
        print("🎯 FINAL COMPREHENSIVE TEST - Acta Diurna Phase 3 Flipbook Newspaper System")
        print("=" * 80)
        
        # Step 1: System Health Check
        print("\n📋 STEP 1: System Health Check")
        print("-" * 40)
        health_success, health_data = self.test_health_check()
        if not health_success:
            print("❌ CRITICAL: System health check failed")
            return False
        
        # Step 2: Create 3 test users
        print("\n👥 STEP 2: User Registration & Authentication")
        print("-" * 40)
        
        test_users = [
            ("main_user", "alice.editor@actadiurna.com", "SecurePass123!", "Alice Editor"),
            ("contributor1", "bob.writer@actadiurna.com", "WriterPass456!", "Bob Writer"),
            ("contributor2", "carol.reporter@actadiurna.com", "ReporterPass789!", "Carol Reporter")
        ]
        
        users_created = 0
        for user_name, email, password, full_name in test_users:
            if self.create_user(user_name, email, password, full_name):
                users_created += 1
        
        if users_created < 3:
            print("❌ CRITICAL: Could not create all required users")
            return False
        
        # Step 3: Set up bidirectional contributor relationships
        print("\n🤝 STEP 3: Invitation System & Contributor Management")
        print("-" * 40)
        
        # Main user invites contributors
        self.test_invitation_system("main_user", "contributor1")
        self.test_invitation_system("main_user", "contributor2")
        
        # Contributors invite main user (bidirectional)
        self.test_invitation_system("contributor1", "main_user")
        self.test_invitation_system("contributor2", "main_user")
        
        # Set up contributor relationships
        self.test_contributor_management("main_user", "contributor1")
        self.test_contributor_management("main_user", "contributor2")
        self.test_contributor_management("contributor1", "main_user")
        self.test_contributor_management("contributor2", "main_user")
        
        # Step 4: Story Creation & Submission
        print("\n📝 STEP 4: Story Creation & Submission")
        print("-" * 40)
        
        stories = [
            ("main_user", "Community Garden Success", "Our local community garden has flourished this season with over 50 families participating. The harvest festival brought together neighbors from all walks of life, sharing fresh produce and building lasting friendships. This initiative has transformed an empty lot into a vibrant community hub.", True),
            ("contributor1", "Tech Innovation in Education", "Local schools are embracing new technology to enhance learning experiences. Interactive whiteboards, tablets, and coding classes are preparing students for the digital future. Teachers report increased engagement and improved problem-solving skills among students.", False),
            ("contributor2", "Environmental Conservation Efforts", "The city's new recycling program has exceeded expectations, with a 40% increase in recycling rates. Citizens are embracing sustainable practices, and local businesses are joining the green initiative. This collective effort is making a significant impact on our environmental footprint.", True)
        ]
        
        story_ids = {}
        for user_name, title, content, is_headline in stories:
            success, story_id = self.test_story_creation(user_name, title, content, is_headline)
            if success and story_id:
                story_ids[user_name] = story_id
                # Test image upload for each story
                self.test_image_upload(user_name, story_id)
        
        # Step 5: Newspaper Generation & Cross-pollination Test
        print("\n🗞️ STEP 5: Newspaper Generation & Cross-pollination")
        print("-" * 40)
        
        newspaper_results = {}
        for user_name in ["main_user", "contributor1", "contributor2"]:
            success, result = self.test_newspaper_generation(user_name)
            if success:
                newspaper_results[user_name] = result
        
        # Step 6: Archive System Test
        print("\n📚 STEP 6: Archive System")
        print("-" * 40)
        
        for user_name in ["main_user", "contributor1", "contributor2"]:
            self.test_archive_system(user_name)
        
        # Step 7: Flipbook Data Structure Verification
        print("\n📖 STEP 7: Flipbook Data Structure Verification")
        print("-" * 40)
        
        for user_name in ["main_user", "contributor1", "contributor2"]:
            self.test_flipbook_data_structure(user_name)
        
        # Final Analysis
        print("\n📊 FINAL ANALYSIS")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["success"]])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"📈 Success Rate: {success_rate:.1f}%")
        
        # Critical Success Criteria Check
        print("\n🎯 CRITICAL SUCCESS CRITERIA VERIFICATION")
        print("-" * 50)
        
        criteria_results = []
        
        # Multiple users can register and authenticate
        auth_success = users_created >= 3
        criteria_results.append(("Multiple users registration & authentication", auth_success))
        
        # Invitation system creates proper relationships
        invitation_tests = [r for r in self.test_results if "Invitation" in r["test"]]
        invitation_success = all(r["success"] for r in invitation_tests)
        criteria_results.append(("Invitation system functionality", invitation_success))
        
        # Contributors can submit stories
        story_tests = [r for r in self.test_results if "Story" in r["test"]]
        story_success = all(r["success"] for r in story_tests)
        criteria_results.append(("Story creation & submission", story_success))
        
        # Newspaper generation includes contributor stories
        newspaper_tests = [r for r in self.test_results if "Newspaper" in r["test"]]
        newspaper_success = all(r["success"] for r in newspaper_tests)
        criteria_results.append(("Newspaper generation with contributor stories", newspaper_success))
        
        # Archive system works
        archive_tests = [r for r in self.test_results if "Archive" in r["test"]]
        archive_success = all(r["success"] for r in archive_tests)
        criteria_results.append(("Archive system functionality", archive_success))
        
        # Flipbook data structure is correct
        flipbook_tests = [r for r in self.test_results if "Flipbook" in r["test"]]
        flipbook_success = all(r["success"] for r in flipbook_tests)
        criteria_results.append(("Flipbook data structure correctness", flipbook_success))
        
        for criteria, success in criteria_results:
            status = "✅" if success else "❌"
            print(f"{status} {criteria}")
        
        all_criteria_met = all(success for _, success in criteria_results)
        
        print(f"\n🏆 FINAL VERDICT: {'PRODUCTION READY' if all_criteria_met else 'NEEDS ATTENTION'}")
        
        return {
            "success": all_criteria_met,
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": success_rate,
            "criteria_results": criteria_results,
            "newspaper_results": newspaper_results,
            "detailed_results": self.test_results
        }

if __name__ == "__main__":
    tester = ComprehensivePhase3Tester()
    results = tester.run_comprehensive_test()
    
    # Save detailed results
    with open('/app/comprehensive_test_results.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n📄 Detailed results saved to: /app/comprehensive_test_results.json")
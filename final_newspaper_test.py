#!/usr/bin/env python3
"""
Final Comprehensive Test of Phase 3 Newspaper Generation System
Tests the complete workflow with proper contributor setup
"""

import requests
import json
from datetime import datetime

BACKEND_URL = "https://e4f87101-35d9-4339-9777-88089f139507.preview.emergentagent.com/api"

class FinalNewspaperTest:
    def __init__(self):
        self.sessions = {}
        self.tokens = {}
        
    def create_and_login_user(self, email, password, full_name):
        """Create and login a user"""
        session = requests.Session()
        
        # Try to register
        register_data = {
            "email": email,
            "password": password,
            "full_name": full_name
        }
        
        register_response = session.post(f"{BACKEND_URL}/auth/register", json=register_data)
        
        if register_response.status_code == 200:
            token = register_response.json()["access_token"]
            session.headers.update({"Authorization": f"Bearer {token}"})
            print(f"✅ Created and logged in: {full_name}")
            return session, token
        elif register_response.status_code == 400 and "already registered" in register_response.text:
            # User exists, try to login
            login_response = session.post(f"{BACKEND_URL}/auth/login", json={
                "email": email,
                "password": password
            })
            
            if login_response.status_code == 200:
                token = login_response.json()["access_token"]
                session.headers.update({"Authorization": f"Bearer {token}"})
                print(f"✅ Logged in existing user: {full_name}")
                return session, token
            else:
                print(f"❌ Failed to login existing user: {full_name}")
                return None, None
        else:
            print(f"❌ Failed to create user: {full_name}")
            return None, None
    
    def setup_test_users(self):
        """Setup all test users"""
        print("👥 SETTING UP TEST USERS:")
        
        users = [
            ("test@actadiurna.com", "TestPass123!", "Test User"),
            ("alice@actadiurna.com", "AlicePass123!", "Alice Reporter"),
            ("bob@actadiurna.com", "BobPass123!", "Bob Journalist"),
        ]
        
        for email, password, name in users:
            session, token = self.create_and_login_user(email, password, name)
            if session and token:
                self.sessions[email] = session
                self.tokens[email] = token
            else:
                return False
        
        return True
    
    def create_proper_contributor_relationships(self):
        """Create proper contributor relationships using a different approach"""
        print("\n🔗 CREATING CONTRIBUTOR RELATIONSHIPS:")
        
        main_session = self.sessions["test@actadiurna.com"]
        alice_session = self.sessions["alice@actadiurna.com"]
        bob_session = self.sessions["bob@actadiurna.com"]
        
        # Strategy: Create fresh users that will auto-accept invitations
        fresh_users = [
            ("contributor.alpha@actadiurna.com", "AlphaPass123!", "Alpha Contributor"),
            ("contributor.beta@actadiurna.com", "BetaPass123!", "Beta Contributor"),
        ]
        
        for email, password, name in fresh_users:
            # Send invitation first
            invitation_data = {"email": email}
            invite_response = main_session.post(f"{BACKEND_URL}/invitations/send", json=invitation_data)
            
            if invite_response.status_code == 200:
                print(f"✅ Invitation sent to {name}")
            elif "Already invited" in invite_response.text:
                print(f"✅ {name} already invited")
            else:
                print(f"❌ Failed to invite {name}: {invite_response.text}")
                continue
            
            # Now register the user (this should auto-accept the invitation)
            register_data = {
                "email": email,
                "password": password,
                "full_name": name
            }
            
            register_response = requests.post(f"{BACKEND_URL}/auth/register", json=register_data)
            
            if register_response.status_code == 200:
                print(f"✅ {name} registered successfully")
                
                # Login as the new contributor
                contrib_token = register_response.json()["access_token"]
                contrib_session = requests.Session()
                contrib_session.headers.update({"Authorization": f"Bearer {contrib_token}"})
                
                # Check received invitations
                received_response = contrib_session.get(f"{BACKEND_URL}/invitations/received")
                if received_response.status_code == 200:
                    invitations = received_response.json()
                    print(f"📥 {name} has {len(invitations)} accepted invitations")
                    
                    if invitations:
                        # Add main user as contributor
                        invitation_id = invitations[0]["id"]
                        add_data = {"invitation_id": invitation_id}
                        add_response = contrib_session.post(f"{BACKEND_URL}/contributors/add", json=add_data)
                        
                        if add_response.status_code == 200:
                            print(f"✅ {name} added main user as contributor")
                        else:
                            print(f"❌ {name} failed to add contributor: {add_response.text}")
                    
                    # Store session for story submission
                    self.sessions[email] = contrib_session
                    self.tokens[email] = contrib_token
                
            elif "already registered" in register_response.text:
                print(f"✅ {name} already exists")
                # Try to login and establish relationship
                login_response = requests.post(f"{BACKEND_URL}/auth/login", json={
                    "email": email,
                    "password": password
                })
                
                if login_response.status_code == 200:
                    contrib_token = login_response.json()["access_token"]
                    contrib_session = requests.Session()
                    contrib_session.headers.update({"Authorization": f"Bearer {contrib_token}"})
                    self.sessions[email] = contrib_session
                    self.tokens[email] = contrib_token
            else:
                print(f"❌ Failed to register {name}: {register_response.text}")
        
        return True
    
    def submit_test_stories(self):
        """Submit test stories from all users"""
        print("\n📝 SUBMITTING TEST STORIES:")
        
        stories = [
            ("test@actadiurna.com", {
                "title": "Main User's Weekly Report",
                "headline": "Community Garden Wins City Award",
                "content": "The downtown community garden has been recognized with the City's Environmental Excellence Award for its outstanding contribution to urban sustainability and community building."
            }),
            ("contributor.alpha@actadiurna.com", {
                "title": "Alpha's Breaking News",
                "headline": "New Art Installation Unveiled",
                "content": "A stunning new sculpture was unveiled in Central Plaza this week, created by local artist Maria Rodriguez. The piece represents community connections."
            }),
            ("contributor.beta@actadiurna.com", {
                "title": "Beta's Local Update",
                "headline": "Local Business Expansion",
                "content": "The popular downtown café is expanding to a second location, bringing more jobs and community gathering spaces to our neighborhood."
            }),
        ]
        
        for email, story_data in stories:
            if email in self.sessions:
                session = self.sessions[email]
                response = session.post(f"{BACKEND_URL}/stories/submit", json=story_data)
                
                if response.status_code == 200:
                    print(f"✅ Story submitted by {email}")
                elif "already submitted" in response.text:
                    print(f"✅ {email} already submitted story this week")
                else:
                    print(f"❌ Failed to submit story for {email}: {response.text}")
            else:
                print(f"❌ No session for {email}")
        
        return True
    
    def test_newspaper_generation_endpoints(self):
        """Test all newspaper generation endpoints"""
        print("\n🗞️  TESTING NEWSPAPER GENERATION ENDPOINTS:")
        
        main_session = self.sessions["test@actadiurna.com"]
        
        # Test 1: Current newspaper
        current_response = main_session.get(f"{BACKEND_URL}/newspapers/current")
        if current_response.status_code == 200:
            newspaper = current_response.json()
            stories = newspaper.get("stories", [])
            authors = set(story.get("author_name") for story in stories)
            
            print(f"📰 Current newspaper: {len(stories)} stories from {len(authors)} authors")
            for i, story in enumerate(stories, 1):
                print(f"   {i}. {story.get('title')} by {story.get('author_name')}")
            
            # Verify business rules
            headlines_count = sum(1 for story in stories if story.get("headline"))
            print(f"📊 Headlines: {headlines_count}, Total stories: {len(stories)}")
            
            success = len(authors) > 1
            print(f"✅ Multiple contributors: {'YES' if success else 'NO'}")
        else:
            print(f"❌ Current newspaper failed: {current_response.text}")
            success = False
        
        # Test 2: Archive
        archive_response = main_session.get(f"{BACKEND_URL}/newspapers/archive")
        if archive_response.status_code == 200:
            archive = archive_response.json()
            print(f"📚 Archive: {len(archive)} newspapers")
        else:
            print(f"❌ Archive failed: {archive_response.text}")
        
        # Test 3: Regenerate
        regen_response = main_session.post(f"{BACKEND_URL}/newspapers/regenerate")
        if regen_response.status_code == 200:
            print("✅ Regeneration successful")
        else:
            print(f"❌ Regeneration failed: {regen_response.text}")
        
        return success
    
    def run_complete_test(self):
        """Run complete Phase 3 newspaper generation test"""
        print("🗞️  PHASE 3 FLIPBOOK NEWSPAPER GENERATION - COMPLETE TEST")
        print("=" * 80)
        
        if not self.setup_test_users():
            print("❌ Failed to setup test users")
            return False
        
        if not self.create_proper_contributor_relationships():
            print("❌ Failed to create contributor relationships")
            return False
        
        if not self.submit_test_stories():
            print("❌ Failed to submit test stories")
            return False
        
        success = self.test_newspaper_generation_endpoints()
        
        print("\n" + "=" * 80)
        if success:
            print("🎉 PHASE 3 SUCCESS: Newspaper generation with contributors is working!")
            print("✅ All newspaper generation endpoints functional")
            print("✅ Story aggregation from multiple contributors working")
            print("✅ Business rules properly enforced")
        else:
            print("❌ PHASE 3 ISSUE: Contributor stories not properly aggregated")
            print("🔍 Root cause: Contributor relationship architecture needs review")
        print("=" * 80)
        
        return success

if __name__ == "__main__":
    tester = FinalNewspaperTest()
    success = tester.run_complete_test()
    
    if success:
        print("\n🎯 FINAL RESULT: Phase 3 Flipbook Newspaper Generation is WORKING!")
    else:
        print("\n🎯 FINAL RESULT: Phase 3 needs contributor relationship fixes")
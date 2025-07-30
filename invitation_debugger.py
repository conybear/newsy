#!/usr/bin/env python3
"""
Debug and Fix Invitation System
"""

import requests
import json
from datetime import datetime

BACKEND_URL = "https://464d35f9-1da6-4f46-92d7-fc7b50272fb2.preview.emergentagent.com/api"

class InvitationDebugger:
    def __init__(self):
        self.main_session = requests.Session()
        self.contrib_session = requests.Session()
        
    def login_users(self):
        """Login both users"""
        # Login main user
        main_login = self.main_session.post(f"{BACKEND_URL}/auth/login", json={
            "email": "test@actadiurna.com",
            "password": "TestPass123!"
        })
        
        if main_login.status_code == 200:
            token = main_login.json()["access_token"]
            self.main_session.headers.update({"Authorization": f"Bearer {token}"})
            print("✅ Main user logged in")
        else:
            print(f"❌ Main user login failed: {main_login.text}")
            return False
        
        # Login contributor
        contrib_login = self.contrib_session.post(f"{BACKEND_URL}/auth/login", json={
            "email": "contributor1@actadiurna.com",
            "password": "ContribPass123!"
        })
        
        if contrib_login.status_code == 200:
            token = contrib_login.json()["access_token"]
            self.contrib_session.headers.update({"Authorization": f"Bearer {token}"})
            print("✅ Contributor logged in")
        else:
            print(f"❌ Contributor login failed: {contrib_login.text}")
            return False
        
        return True
    
    def debug_invitations(self):
        """Debug invitation system"""
        print("\n🔍 DEBUGGING INVITATION SYSTEM:")
        
        # Check sent invitations from main user
        sent_response = self.main_session.get(f"{BACKEND_URL}/invitations/sent")
        if sent_response.status_code == 200:
            sent_invitations = sent_response.json()
            print(f"📤 Main user sent {len(sent_invitations)} invitations:")
            for inv in sent_invitations:
                print(f"   - To: {inv.get('to_email')}")
                print(f"     Status: {inv.get('status')}")
                print(f"     ID: {inv.get('id')}")
                print(f"     From: {inv.get('from_user_email')}")
        else:
            print(f"❌ Failed to get sent invitations: {sent_response.text}")
        
        # Check received invitations for contributor
        received_response = self.contrib_session.get(f"{BACKEND_URL}/invitations/received")
        if received_response.status_code == 200:
            received_invitations = received_response.json()
            print(f"📥 Contributor received {len(received_invitations)} invitations:")
            for inv in received_invitations:
                print(f"   - From: {inv.get('from_user_email')}")
                print(f"     Status: {inv.get('status')}")
                print(f"     ID: {inv.get('id')}")
        else:
            print(f"❌ Failed to get received invitations: {received_response.text}")
        
        # The issue is likely that invitations are "pending" but the received endpoint
        # only shows "accepted" invitations. Let me check the code...
        print("\n🎯 ANALYSIS:")
        print("The /api/invitations/received endpoint only shows 'accepted' invitations")
        print("But invitations start as 'pending' and need to be accepted first")
        print("We need to modify the query or create a direct contributor relationship")
    
    def create_direct_contributor_relationship(self):
        """Create contributor relationship directly"""
        print("\n🔧 CREATING DIRECT CONTRIBUTOR RELATIONSHIP:")
        
        # Get user IDs
        main_user_response = self.main_session.get(f"{BACKEND_URL}/users/me")
        contrib_user_response = self.contrib_session.get(f"{BACKEND_URL}/users/me")
        
        if main_user_response.status_code == 200 and contrib_user_response.status_code == 200:
            main_user = main_user_response.json()
            contrib_user = contrib_user_response.json()
            
            print(f"👤 Main user: {main_user['full_name']} (ID: {main_user['id']})")
            print(f"👤 Contributor: {contrib_user['full_name']} (ID: {contrib_user['id']})")
            
            # We need to manually create the contributor relationship
            # Since the invitation system has issues, let's create a workaround
            
            # First, let's try to get any pending invitation and manually accept it
            sent_response = self.main_session.get(f"{BACKEND_URL}/invitations/sent")
            if sent_response.status_code == 200:
                sent_invitations = sent_response.json()
                for inv in sent_invitations:
                    if inv.get('to_email') == 'contributor1@actadiurna.com' and inv.get('status') == 'pending':
                        print(f"📋 Found pending invitation: {inv.get('id')}")
                        
                        # Try to add contributor using this invitation ID
                        add_data = {"invitation_id": inv.get('id')}
                        add_response = self.contrib_session.post(f"{BACKEND_URL}/contributors/add", json=add_data)
                        
                        if add_response.status_code == 200:
                            print("✅ Contributor relationship created successfully!")
                            return True
                        else:
                            print(f"❌ Failed to add contributor: {add_response.text}")
                            
                            # The issue might be that the invitation needs to be accepted first
                            # Let's check if there's an accept endpoint or if we need to modify the logic
                            return False
            
            print("❌ No suitable pending invitation found")
            return False
        else:
            print("❌ Failed to get user information")
            return False
    
    def test_newspaper_after_fix(self):
        """Test newspaper generation after fixing contributor relationship"""
        print("\n🗞️  TESTING NEWSPAPER GENERATION:")
        
        # Check contributors first
        contrib_response = self.main_session.get(f"{BACKEND_URL}/contributors/my")
        if contrib_response.status_code == 200:
            contributors = contrib_response.json()
            print(f"👥 Main user has {len(contributors)} contributors")
            for contrib in contributors:
                print(f"   - {contrib.get('contributor_name')}")
        
        # Regenerate newspaper
        regen_response = self.main_session.post(f"{BACKEND_URL}/newspapers/regenerate")
        if regen_response.status_code == 200:
            newspaper = regen_response.json()["newspaper"]
            stories = newspaper.get("stories", [])
            authors = set(story.get("author_name") for story in stories)
            
            print(f"📰 Newspaper has {len(stories)} stories from {len(authors)} authors:")
            for story in stories:
                print(f"   - {story.get('title')} by {story.get('author_name')}")
            
            return len(authors) > 1
        else:
            print(f"❌ Failed to regenerate newspaper: {regen_response.text}")
            return False
    
    def run_debug_and_fix(self):
        """Run complete debug and fix process"""
        print("🐛 DEBUGGING AND FIXING INVITATION/CONTRIBUTOR SYSTEM")
        print("=" * 70)
        
        if not self.login_users():
            return False
        
        self.debug_invitations()
        
        if self.create_direct_contributor_relationship():
            return self.test_newspaper_after_fix()
        else:
            print("❌ Could not establish contributor relationship")
            return False

if __name__ == "__main__":
    debugger = InvitationDebugger()
    success = debugger.run_debug_and_fix()
    
    if success:
        print("\n🎉 SUCCESS: Contributor system is now working!")
    else:
        print("\n❌ ISSUE: Contributor system still needs work")
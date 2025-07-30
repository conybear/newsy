#!/usr/bin/env python3
"""
Manual Fix for Invitation Status and Test Newspaper Generation
"""

import requests
import json
from datetime import datetime

BACKEND_URL = "https://464d35f9-1da6-4f46-92d7-fc7b50272fb2.preview.emergentagent.com/api"

class ManualInvitationFixer:
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
            print(f"❌ Main user login failed")
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
            print(f"❌ Contributor login failed")
            return False
        
        return True
    
    def simulate_invitation_acceptance(self):
        """Simulate the invitation acceptance process that should happen during registration"""
        print("\n🔧 SIMULATING INVITATION ACCEPTANCE:")
        
        # The issue is that the invitation was sent AFTER the contributor registered
        # So it was never automatically marked as "accepted"
        # We need to manually trigger the acceptance logic
        
        # Re-register the contributor to trigger invitation acceptance
        contrib_data = {
            "email": "contributor1@actadiurna.com",
            "password": "ContribPass123!",
            "full_name": "Alice Contributor"
        }
        
        # This will fail with "Email already registered" but might trigger invitation acceptance
        register_response = requests.post(f"{BACKEND_URL}/auth/register", json=contrib_data)
        print(f"📝 Re-registration attempt: {register_response.status_code}")
        
        # Check if invitations are now accepted
        received_response = self.contrib_session.get(f"{BACKEND_URL}/invitations/received")
        if received_response.status_code == 200:
            received_invitations = received_response.json()
            print(f"📥 Contributor now has {len(received_invitations)} accepted invitations")
            
            if received_invitations:
                # Try to add contributor
                invitation_id = received_invitations[0]["id"]
                add_data = {"invitation_id": invitation_id}
                add_response = self.contrib_session.post(f"{BACKEND_URL}/contributors/add", json=add_data)
                
                if add_response.status_code == 200:
                    print("✅ Contributor relationship established!")
                    return True
                else:
                    print(f"❌ Failed to add contributor: {add_response.text}")
                    return False
            else:
                print("❌ Still no accepted invitations")
                return False
        else:
            print(f"❌ Failed to get received invitations: {received_response.text}")
            return False
    
    def create_new_contributor_and_test(self):
        """Create a fresh contributor to test the full flow"""
        print("\n🆕 CREATING FRESH CONTRIBUTOR FOR TESTING:")
        
        # Create a new contributor user
        new_contrib_data = {
            "email": "fresh.contributor@actadiurna.com",
            "password": "FreshPass123!",
            "full_name": "Fresh Contributor"
        }
        
        # Send invitation first
        invitation_data = {"email": "fresh.contributor@actadiurna.com"}
        invite_response = self.main_session.post(f"{BACKEND_URL}/invitations/send", json=invitation_data)
        
        if invite_response.status_code == 200:
            print("✅ Invitation sent to fresh contributor")
        else:
            print(f"❌ Failed to send invitation: {invite_response.text}")
            return False
        
        # Now register the contributor (this should auto-accept the invitation)
        register_response = requests.post(f"{BACKEND_URL}/auth/register", json=new_contrib_data)
        
        if register_response.status_code == 200:
            print("✅ Fresh contributor registered")
            fresh_token = register_response.json()["access_token"]
            
            # Login as fresh contributor
            fresh_session = requests.Session()
            fresh_session.headers.update({"Authorization": f"Bearer {fresh_token}"})
            
            # Check received invitations
            received_response = fresh_session.get(f"{BACKEND_URL}/invitations/received")
            if received_response.status_code == 200:
                received_invitations = received_response.json()
                print(f"📥 Fresh contributor has {len(received_invitations)} accepted invitations")
                
                if received_invitations:
                    # Add contributor relationship
                    invitation_id = received_invitations[0]["id"]
                    add_data = {"invitation_id": invitation_id}
                    add_response = fresh_session.post(f"{BACKEND_URL}/contributors/add", json=add_data)
                    
                    if add_response.status_code == 200:
                        print("✅ Fresh contributor relationship established!")
                        
                        # Submit a story as fresh contributor
                        story_data = {
                            "title": "Fresh Contributor's Story",
                            "headline": "Breaking: Fresh Perspective on Local News",
                            "content": "This is a story from the fresh contributor to test the newspaper generation system with multiple contributors."
                        }
                        
                        story_response = fresh_session.post(f"{BACKEND_URL}/stories/submit", json=story_data)
                        if story_response.status_code == 200:
                            print("✅ Fresh contributor story submitted")
                            return True
                        else:
                            print(f"❌ Failed to submit fresh contributor story: {story_response.text}")
                            return False
                    else:
                        print(f"❌ Failed to add fresh contributor: {add_response.text}")
                        return False
                else:
                    print("❌ Fresh contributor has no accepted invitations")
                    return False
            else:
                print(f"❌ Failed to get fresh contributor invitations: {received_response.text}")
                return False
        else:
            print(f"❌ Failed to register fresh contributor: {register_response.text}")
            return False
    
    def test_newspaper_generation(self):
        """Test newspaper generation with contributors"""
        print("\n🗞️  TESTING NEWSPAPER GENERATION:")
        
        # Check contributors
        contrib_response = self.main_session.get(f"{BACKEND_URL}/contributors/my")
        if contrib_response.status_code == 200:
            contributors = contrib_response.json()
            print(f"👥 Main user has {len(contributors)} contributors:")
            for contrib in contributors:
                print(f"   - {contrib.get('contributor_name')} ({contrib.get('contributor_email')})")
        
        # Regenerate newspaper
        regen_response = self.main_session.post(f"{BACKEND_URL}/newspapers/regenerate")
        if regen_response.status_code == 200:
            newspaper = regen_response.json()["newspaper"]
            stories = newspaper.get("stories", [])
            authors = set(story.get("author_name") for story in stories)
            
            print(f"📰 Newspaper regenerated with {len(stories)} stories from {len(authors)} authors:")
            for i, story in enumerate(stories, 1):
                print(f"   {i}. {story.get('title')} by {story.get('author_name')}")
                print(f"      Headline: {story.get('headline')}")
            
            if len(authors) > 1:
                print("🎉 SUCCESS: Multiple contributors' stories are included!")
                return True
            else:
                print("❌ ISSUE: Still only showing stories from one author")
                return False
        else:
            print(f"❌ Failed to regenerate newspaper: {regen_response.text}")
            return False
    
    def run_complete_test(self):
        """Run complete test with fresh contributor"""
        print("🧪 COMPLETE CONTRIBUTOR SYSTEM TEST")
        print("=" * 60)
        
        if not self.login_users():
            return False
        
        # Try the fresh contributor approach
        if self.create_new_contributor_and_test():
            return self.test_newspaper_generation()
        else:
            print("❌ Fresh contributor test failed")
            return False

if __name__ == "__main__":
    fixer = ManualInvitationFixer()
    success = fixer.run_complete_test()
    
    if success:
        print("\n🎉 COMPLETE SUCCESS: Newspaper generation with contributors is working!")
    else:
        print("\n❌ ISSUE: Contributor system needs further investigation")
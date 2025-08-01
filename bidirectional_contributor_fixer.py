#!/usr/bin/env python3
"""
Fix Contributor Relationship Logic - Create Bidirectional Relationships
"""

import requests
import json
from datetime import datetime

BACKEND_URL = "https://e4f87101-35d9-4339-9777-88089f139507.preview.emergentagent.com/api"

class BidirectionalContributorFixer:
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
            return False
        
        # Login fresh contributor
        contrib_login = self.contrib_session.post(f"{BACKEND_URL}/auth/login", json={
            "email": "fresh.contributor@actadiurna.com",
            "password": "FreshPass123!"
        })
        
        if contrib_login.status_code == 200:
            token = contrib_login.json()["access_token"]
            self.contrib_session.headers.update({"Authorization": f"Bearer {token}"})
            print("✅ Fresh contributor logged in")
        else:
            return False
        
        return True
    
    def create_reverse_contributor_relationship(self):
        """Create the reverse contributor relationship"""
        print("\n🔄 CREATING REVERSE CONTRIBUTOR RELATIONSHIP:")
        
        # The fresh contributor should send an invitation back to the main user
        # This will create the relationship in the correct direction
        
        invitation_data = {"email": "test@actadiurna.com"}
        invite_response = self.contrib_session.post(f"{BACKEND_URL}/invitations/send", json=invitation_data)
        
        if invite_response.status_code == 200:
            print("✅ Reverse invitation sent from contributor to main user")
        elif "Already invited" in invite_response.text:
            print("✅ Reverse invitation already exists")
        else:
            print(f"❌ Failed to send reverse invitation: {invite_response.text}")
            return False
        
        # Main user should now have a received invitation
        received_response = self.main_session.get(f"{BACKEND_URL}/invitations/received")
        if received_response.status_code == 200:
            received_invitations = received_response.json()
            print(f"📥 Main user has {len(received_invitations)} received invitations")
            
            if received_invitations:
                # Find invitation from fresh contributor
                fresh_invitation = None
                for inv in received_invitations:
                    if inv.get('from_user_email') == 'fresh.contributor@actadiurna.com':
                        fresh_invitation = inv
                        break
                
                if fresh_invitation:
                    # Main user adds fresh contributor as their contributor
                    add_data = {"invitation_id": fresh_invitation["id"]}
                    add_response = self.main_session.post(f"{BACKEND_URL}/contributors/add", json=add_data)
                    
                    if add_response.status_code == 200:
                        print("✅ Main user now has fresh contributor as their contributor!")
                        return True
                    else:
                        print(f"❌ Failed to add reverse contributor: {add_response.text}")
                        return False
                else:
                    print("❌ No invitation from fresh contributor found")
                    return False
            else:
                print("❌ Main user has no received invitations")
                return False
        else:
            print(f"❌ Failed to get main user's received invitations: {received_response.text}")
            return False
    
    def test_final_newspaper_generation(self):
        """Test newspaper generation with proper contributor relationship"""
        print("\n🗞️  FINAL NEWSPAPER GENERATION TEST:")
        
        # Check main user's contributors
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
            
            print(f"📰 Final newspaper has {len(stories)} stories from {len(authors)} authors:")
            for i, story in enumerate(stories, 1):
                print(f"   {i}. {story.get('title')} by {story.get('author_name')}")
                print(f"      Headline: {story.get('headline')}")
            
            if len(authors) > 1:
                print("🎉 FINAL SUCCESS: Multiple contributors' stories are included!")
                return True
            else:
                print("❌ FINAL ISSUE: Still only showing stories from one author")
                return False
        else:
            print(f"❌ Failed to regenerate newspaper: {regen_response.text}")
            return False
    
    def run_bidirectional_fix(self):
        """Run complete bidirectional contributor fix"""
        print("🔄 BIDIRECTIONAL CONTRIBUTOR RELATIONSHIP FIX")
        print("=" * 60)
        
        if not self.login_users():
            print("❌ Failed to login users")
            return False
        
        if not self.create_reverse_contributor_relationship():
            print("❌ Failed to create reverse contributor relationship")
            return False
        
        return self.test_final_newspaper_generation()

if __name__ == "__main__":
    fixer = BidirectionalContributorFixer()
    success = fixer.run_bidirectional_fix()
    
    if success:
        print("\n🎉 ULTIMATE SUCCESS: Bidirectional contributor system is working!")
        print("📰 Newspaper generation now includes stories from all contributors!")
    else:
        print("\n❌ FINAL ISSUE: Contributor system architecture needs redesign")
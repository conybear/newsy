#!/usr/bin/env python3
"""
Fix Contributor Relationship and Test Newspaper Generation
"""

import requests
import json
from datetime import datetime

BACKEND_URL = "https://464d35f9-1da6-4f46-92d7-fc7b50272fb2.preview.emergentagent.com/api"

class ContributorFixer:
    def __init__(self):
        self.main_session = requests.Session()
        self.contrib_session = requests.Session()
        self.main_token = None
        self.contrib_token = None
        
    def login_main_user(self):
        """Login as test@actadiurna.com"""
        login_data = {
            "email": "test@actadiurna.com",
            "password": "TestPass123!"
        }
        
        response = self.main_session.post(f"{BACKEND_URL}/auth/login", json=login_data)
        if response.status_code == 200:
            data = response.json()
            self.main_token = data["access_token"]
            self.main_session.headers.update({"Authorization": f"Bearer {self.main_token}"})
            print(f"✅ Main user logged in: {data['user']['full_name']}")
            return True
        else:
            print(f"❌ Main user login failed: {response.text}")
            return False
    
    def login_contributor(self):
        """Login as contributor1@actadiurna.com"""
        login_data = {
            "email": "contributor1@actadiurna.com",
            "password": "ContribPass123!"
        }
        
        response = self.contrib_session.post(f"{BACKEND_URL}/auth/login", json=login_data)
        if response.status_code == 200:
            data = response.json()
            self.contrib_token = data["access_token"]
            self.contrib_session.headers.update({"Authorization": f"Bearer {self.contrib_token}"})
            print(f"✅ Contributor logged in: {data['user']['full_name']}")
            return True
        else:
            print(f"❌ Contributor login failed: {response.text}")
            return False
    
    def establish_contributor_relationship(self):
        """Properly establish contributor relationship"""
        print("\n🔗 Establishing Contributor Relationship:")
        
        # Step 1: Main user sends invitation (if not already sent)
        invitation_data = {"email": "contributor1@actadiurna.com"}
        invite_response = self.main_session.post(f"{BACKEND_URL}/invitations/send", json=invitation_data)
        if invite_response.status_code == 200:
            print("✅ Invitation sent")
        elif "Already invited" in invite_response.text:
            print("✅ Invitation already sent")
        else:
            print(f"❌ Failed to send invitation: {invite_response.text}")
            return False
        
        # Step 2: Contributor gets received invitations
        received_response = self.contrib_session.get(f"{BACKEND_URL}/invitations/received")
        if received_response.status_code == 200:
            invitations = received_response.json()
            print(f"📥 Contributor has {len(invitations)} received invitations")
            
            if invitations:
                # Step 3: Contributor adds main user as contributor
                invitation_id = invitations[0]["id"]
                add_data = {"invitation_id": invitation_id}
                add_response = self.contrib_session.post(f"{BACKEND_URL}/contributors/add", json=add_data)
                if add_response.status_code == 200:
                    print("✅ Contributor relationship established")
                elif "Already added" in add_response.text:
                    print("✅ Contributor relationship already exists")
                else:
                    print(f"❌ Failed to add contributor: {add_response.text}")
                    return False
            else:
                print("❌ No invitations found for contributor")
                return False
        else:
            print(f"❌ Failed to get received invitations: {received_response.text}")
            return False
        
        return True
    
    def verify_contributor_relationship(self):
        """Verify the contributor relationship is working"""
        print("\n🔍 Verifying Contributor Relationship:")
        
        # Check main user's contributors
        main_contributors_response = self.main_session.get(f"{BACKEND_URL}/contributors/my")
        if main_contributors_response.status_code == 200:
            main_contributors = main_contributors_response.json()
            print(f"👤 Main user has {len(main_contributors)} contributors:")
            for contrib in main_contributors:
                print(f"   - {contrib.get('contributor_name')} ({contrib.get('contributor_email')})")
        
        # Check contributor's contributors (should include main user)
        contrib_contributors_response = self.contrib_session.get(f"{BACKEND_URL}/contributors/my")
        if contrib_contributors_response.status_code == 200:
            contrib_contributors = contrib_contributors_response.json()
            print(f"👤 Contributor has {len(contrib_contributors)} contributors:")
            for contrib in contrib_contributors:
                print(f"   - {contrib.get('contributor_name')} ({contrib.get('contributor_email')})")
        
        return len(main_contributors) > 0 or len(contrib_contributors) > 0
    
    def test_newspaper_generation(self):
        """Test newspaper generation with contributor stories"""
        print("\n🗞️  Testing Newspaper Generation:")
        
        # Force regenerate newspaper to pick up new contributor relationship
        regen_response = self.main_session.post(f"{BACKEND_URL}/newspapers/regenerate")
        if regen_response.status_code == 200:
            newspaper = regen_response.json()["newspaper"]
            stories = newspaper.get("stories", [])
            print(f"✅ Newspaper regenerated with {len(stories)} stories:")
            
            authors = set()
            for i, story in enumerate(stories, 1):
                author = story.get("author_name")
                authors.add(author)
                headline = story.get("headline", "No headline")
                print(f"   {i}. {story.get('title')} by {author}")
                print(f"      Headline: {headline}")
            
            print(f"📊 Stories from {len(authors)} unique authors: {', '.join(authors)}")
            
            if len(authors) > 1:
                print("✅ SUCCESS: Contributor stories are now included!")
                return True
            else:
                print("❌ ISSUE: Still only showing stories from one author")
                return False
        else:
            print(f"❌ Failed to regenerate newspaper: {regen_response.text}")
            return False
    
    def run_fix_and_test(self):
        """Run complete fix and test process"""
        print("🔧 FIXING CONTRIBUTOR RELATIONSHIP AND TESTING NEWSPAPER GENERATION")
        print("=" * 80)
        
        if not self.login_main_user():
            return False
        
        if not self.login_contributor():
            return False
        
        if not self.establish_contributor_relationship():
            return False
        
        if not self.verify_contributor_relationship():
            print("❌ Contributor relationship verification failed")
            return False
        
        success = self.test_newspaper_generation()
        
        print("\n" + "=" * 80)
        if success:
            print("🎉 SUCCESS: Contributor stories are now appearing in newspapers!")
        else:
            print("❌ ISSUE: Contributor stories still not appearing properly")
        print("=" * 80)
        
        return success

if __name__ == "__main__":
    fixer = ContributorFixer()
    fixer.run_fix_and_test()
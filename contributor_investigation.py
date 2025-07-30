#!/usr/bin/env python3
"""
Deep Investigation of Contributor Stories in Newspaper Generation
"""

import requests
import json
from datetime import datetime

BACKEND_URL = "https://464d35f9-1da6-4f46-92d7-fc7b50272fb2.preview.emergentagent.com/api"

class ContributorInvestigator:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        
    def login_as_test_user(self):
        """Login as test@actadiurna.com"""
        login_data = {
            "email": "test@actadiurna.com",
            "password": "TestPass123!"
        }
        
        response = self.session.post(f"{BACKEND_URL}/auth/login", json=login_data)
        if response.status_code == 200:
            data = response.json()
            self.auth_token = data["access_token"]
            self.session.headers.update({"Authorization": f"Bearer {self.auth_token}"})
            print(f"✅ Logged in as {data['user']['full_name']} ({data['user']['email']})")
            return True
        else:
            print(f"❌ Login failed: {response.text}")
            return False
    
    def check_contributors(self):
        """Check user's contributors"""
        response = self.session.get(f"{BACKEND_URL}/contributors/my")
        if response.status_code == 200:
            contributors = response.json()
            print(f"📋 User has {len(contributors)} contributors:")
            for contrib in contributors:
                print(f"   - {contrib.get('contributor_name')} ({contrib.get('contributor_email')})")
            return contributors
        else:
            print(f"❌ Failed to get contributors: {response.text}")
            return []
    
    def check_invitations_sent(self):
        """Check sent invitations"""
        response = self.session.get(f"{BACKEND_URL}/invitations/sent")
        if response.status_code == 200:
            invitations = response.json()
            print(f"📤 User has sent {len(invitations)} invitations:")
            for inv in invitations:
                print(f"   - To: {inv.get('to_email')}, Status: {inv.get('status')}")
            return invitations
        else:
            print(f"❌ Failed to get sent invitations: {response.text}")
            return []
    
    def check_all_stories_in_db(self):
        """Check all stories in database"""
        # Get current week
        health_response = self.session.get(f"{BACKEND_URL}/health")
        current_week = "2025-W31"
        if health_response.status_code == 200:
            current_week = health_response.json().get("current_week", current_week)
        
        # Check user's stories
        my_stories_response = self.session.get(f"{BACKEND_URL}/stories/my")
        if my_stories_response.status_code == 200:
            my_stories = my_stories_response.json()
            print(f"📚 Test user has {len(my_stories)} submitted stories:")
            for story in my_stories:
                print(f"   - {story.get('title')} (Week: {story.get('week_of')}, Headline: {story.get('headline')})")
        
        # Try to login as contributor and check their stories
        contrib_session = requests.Session()
        contrib_login = contrib_session.post(f"{BACKEND_URL}/auth/login", json={
            "email": "contributor1@actadiurna.com",
            "password": "ContribPass123!"
        })
        
        if contrib_login.status_code == 200:
            contrib_token = contrib_login.json()["access_token"]
            contrib_session.headers.update({"Authorization": f"Bearer {contrib_token}"})
            
            contrib_stories_response = contrib_session.get(f"{BACKEND_URL}/stories/my")
            if contrib_stories_response.status_code == 200:
                contrib_stories = contrib_stories_response.json()
                print(f"📚 Contributor has {len(contrib_stories)} submitted stories:")
                for story in contrib_stories:
                    print(f"   - {story.get('title')} (Week: {story.get('week_of')}, Headline: {story.get('headline')})")
            else:
                print(f"❌ Failed to get contributor stories: {contrib_stories_response.text}")
        else:
            print(f"❌ Failed to login as contributor: {contrib_login.text}")
    
    def check_newspaper_generation_logic(self):
        """Check the newspaper generation logic"""
        # Get current newspaper
        newspaper_response = self.session.get(f"{BACKEND_URL}/newspapers/current")
        if newspaper_response.status_code == 200:
            newspaper = newspaper_response.json()
            print(f"🗞️  Current newspaper for {newspaper.get('week_of')}:")
            print(f"   - Title: {newspaper.get('title')}")
            print(f"   - Stories: {len(newspaper.get('stories', []))}")
            
            for i, story in enumerate(newspaper.get('stories', []), 1):
                print(f"   {i}. {story.get('title')} by {story.get('author_name')} (Headline: {story.get('headline')})")
        else:
            print(f"❌ Failed to get current newspaper: {newspaper_response.text}")
    
    def investigate_user_contributors_relationship(self):
        """Deep dive into user-contributor relationship in database"""
        # Check if the user document has contributors field
        user_response = self.session.get(f"{BACKEND_URL}/users/me")
        if user_response.status_code == 200:
            user_data = user_response.json()
            print(f"👤 User data structure:")
            print(f"   - ID: {user_data.get('id')}")
            print(f"   - Email: {user_data.get('email')}")
            print(f"   - Contributors field: {user_data.get('contributors', 'NOT FOUND')}")
        
        # Check contributors collection
        contributors = self.check_contributors()
        
        # The issue might be that the newspaper generation is looking for contributors
        # in the user document, but they're stored in a separate contributors collection
        print("\n🔍 ANALYSIS:")
        print("The newspaper generation logic in server.py line 591 does:")
        print("contributors = user.get('contributors', [])")
        print("But contributors are stored in a separate 'contributors' collection!")
        print("This explains why only the user's own stories appear in the newspaper.")
        
        return contributors
    
    def run_investigation(self):
        """Run complete investigation"""
        print("🔍 DEEP INVESTIGATION: Contributor Stories in Newspaper Generation")
        print("=" * 80)
        
        if not self.login_as_test_user():
            return
        
        print("\n1. Checking Contributors:")
        contributors = self.check_contributors()
        
        print("\n2. Checking Sent Invitations:")
        self.check_invitations_sent()
        
        print("\n3. Checking All Stories in Database:")
        self.check_all_stories_in_db()
        
        print("\n4. Checking Current Newspaper Generation:")
        self.check_newspaper_generation_logic()
        
        print("\n5. Investigating User-Contributor Relationship:")
        self.investigate_user_contributors_relationship()
        
        print("\n" + "=" * 80)
        print("🎯 ROOT CAUSE IDENTIFIED:")
        print("The newspaper generation logic in server.py (line 591) looks for:")
        print("contributors = user.get('contributors', [])")
        print("But contributors are stored in a separate 'contributors' collection.")
        print("The code should query the contributors collection instead!")
        print("=" * 80)

if __name__ == "__main__":
    investigator = ContributorInvestigator()
    investigator.run_investigation()
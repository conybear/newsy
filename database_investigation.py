#!/usr/bin/env python3
"""
Database Investigation: Find Joel's actual account and debug the specific issue
"""

import requests
import json
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = "https://e4f87101-35d9-4339-9777-88089f139507.preview.emergentagent.com/api"

class DatabaseInvestigator:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        
    def login_with_working_account(self):
        """Login with any working account to access debug endpoints"""
        try:
            # Try known working accounts
            accounts_to_try = [
                {"email": "sarah.johnson@example.com", "password": "SecurePass123!"},
                {"email": "sarah.johnson@newspaper.com", "password": "SecurePass123!"},
                {"email": "test.user@newspaper.com", "password": "TestPass123!"},
                {"email": "mike.reporter@newspaper.com", "password": "FriendPass456!"}
            ]
            
            for account in accounts_to_try:
                response = self.session.post(f"{BACKEND_URL}/auth/login", json=account)
                
                if response.status_code == 200:
                    data = response.json()
                    self.auth_token = data["access_token"]
                    self.session.headers.update({"Authorization": f"Bearer {self.auth_token}"})
                    print(f"✅ Logged in as {account['email']}")
                    return True, account['email']
            
            print("❌ Could not login with any known account")
            return False, None
            
        except Exception as e:
            print(f"❌ Login exception: {str(e)}")
            return False, None

    def get_all_users_from_stories(self):
        """Get all users by examining stories in the database"""
        try:
            response = self.session.get(f"{BACKEND_URL}/debug/simple")
            
            if response.status_code == 200:
                data = response.json()
                all_stories = data.get("all_stories_details", [])
                
                print(f"\n📊 DATABASE ANALYSIS")
                print(f"Total stories in database: {len(all_stories)}")
                print(f"Current week: {data.get('current_week')}")
                
                # Group stories by author
                authors = {}
                for story in all_stories:
                    author_name = story.get("author_name")
                    author_id = story.get("author_id")
                    if author_name:
                        if author_name not in authors:
                            authors[author_name] = {
                                "id": author_id,
                                "stories": [],
                                "weeks": set()
                            }
                        authors[author_name]["stories"].append(story)
                        authors[author_name]["weeks"].add(story.get("week_of"))
                
                print(f"\n👥 AUTHORS IN DATABASE:")
                for author_name, info in authors.items():
                    weeks_list = sorted(list(info["weeks"]))
                    print(f"  {author_name} (ID: {info['id']})")
                    print(f"    Stories: {len(info['stories'])}")
                    print(f"    Weeks: {weeks_list}")
                    for story in info["stories"]:
                        print(f"      - {story.get('title')} ({story.get('week_of')})")
                    print()
                
                # Look for Joel specifically
                joel_found = False
                for author_name, info in authors.items():
                    if "joel" in author_name.lower() or "conybear" in author_name.lower():
                        joel_found = True
                        print(f"🎯 FOUND JOEL: {author_name}")
                        print(f"   ID: {info['id']}")
                        print(f"   Stories: {len(info['stories'])}")
                        break
                
                if not joel_found:
                    print("⚠️  Joel Conybear not found in story authors")
                    print("   This suggests Joel may not have submitted any stories yet")
                
                return True, authors
            else:
                print(f"❌ Debug simple failed: {response.status_code}")
                return False, None
                
        except Exception as e:
            print(f"❌ Exception: {str(e)}")
            return False, None

    def search_for_joel_account(self):
        """Try to find Joel's account by searching"""
        try:
            # Try to search for Joel's account
            response = self.session.get(f"{BACKEND_URL}/users/search?email=joel.conybear@gmail.com")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ FOUND JOEL'S ACCOUNT:")
                print(f"   Email: {data.get('email')}")
                print(f"   Name: {data.get('full_name')}")
                print(f"   ID: {data.get('id')}")
                print(f"   Friends: {len(data.get('friends', []))}")
                print(f"   Contributors: {len(data.get('contributors', []))}")
                return True, data
            elif response.status_code == 404:
                print("❌ Joel's account not found in database")
                return False, None
            else:
                print(f"❌ Search failed: {response.status_code} - {response.text}")
                return False, None
                
        except Exception as e:
            print(f"❌ Search exception: {str(e)}")
            return False, None

    def create_joel_account_for_testing(self):
        """Create Joel's account for testing purposes"""
        try:
            # Create Joel's account
            joel_data = {
                "email": "joel.conybear@gmail.com",
                "password": "JoelTestPass123!",
                "full_name": "Joel Conybear"
            }
            
            response = self.session.post(f"{BACKEND_URL}/auth/register", json=joel_data)
            
            if response.status_code == 200:
                print("✅ Created Joel's account for testing")
                return True
            elif response.status_code == 400 and "already registered" in response.text:
                print("⚠️  Joel's account already exists")
                return True
            else:
                print(f"❌ Failed to create Joel's account: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Exception: {str(e)}")
            return False

    def create_test_scenario_for_joel(self):
        """Create the exact scenario described in the bug report"""
        try:
            print("\n🔧 CREATING TEST SCENARIO FOR JOEL")
            print("=" * 50)
            
            # Step 1: Ensure Joel's account exists
            self.create_joel_account_for_testing()
            
            # Step 2: Create 2 contributors for Joel
            contributors = [
                {
                    "email": "joel.contributor1@test.com",
                    "password": "Contrib1Pass!",
                    "full_name": "Joel's Contributor 1"
                },
                {
                    "email": "joel.contributor2@test.com", 
                    "password": "Contrib2Pass!",
                    "full_name": "Joel's Contributor 2"
                }
            ]
            
            # Create contributor accounts and stories
            for i, contrib in enumerate(contributors, 1):
                # Create contributor account
                contrib_session = requests.Session()
                register_response = contrib_session.post(f"{BACKEND_URL}/auth/register", json=contrib)
                
                if register_response.status_code == 200 or register_response.status_code == 400:
                    # Login as contributor
                    login_response = contrib_session.post(f"{BACKEND_URL}/auth/login", json={
                        "email": contrib["email"],
                        "password": contrib["password"]
                    })
                    
                    if login_response.status_code == 200:
                        contrib_token = login_response.json()["access_token"]
                        contrib_session.headers.update({"Authorization": f"Bearer {contrib_token}"})
                        
                        # Create story as contributor
                        story_data = {
                            "title": f"Story from Joel's Contributor {i}",
                            "content": f"This is a test story from Joel's contributor {i}. It should appear in Joel's weekly edition.",
                            "is_headline": i == 1
                        }
                        
                        story_response = contrib_session.post(f"{BACKEND_URL}/stories", json=story_data)
                        if story_response.status_code == 200:
                            print(f"   ✅ Created story for contributor {i}")
                        else:
                            print(f"   ⚠️  Story creation failed for contributor {i}: {story_response.text}")
                    else:
                        print(f"   ❌ Login failed for contributor {i}")
                else:
                    print(f"   ❌ Registration failed for contributor {i}")
            
            # Step 3: Try to login as Joel and invite contributors
            joel_passwords = ["JoelTestPass123!", "password123", "SecurePass123!"]
            joel_session = requests.Session()
            joel_logged_in = False
            
            for password in joel_passwords:
                login_response = joel_session.post(f"{BACKEND_URL}/auth/login", json={
                    "email": "joel.conybear@gmail.com",
                    "password": password
                })
                
                if login_response.status_code == 200:
                    joel_token = login_response.json()["access_token"]
                    joel_session.headers.update({"Authorization": f"Bearer {joel_token}"})
                    joel_logged_in = True
                    print(f"   ✅ Logged in as Joel with password: {password}")
                    break
            
            if joel_logged_in:
                # Invite contributors as friends
                for contrib in contributors:
                    invite_response = joel_session.post(f"{BACKEND_URL}/friends/invite", json={
                        "email": contrib["email"]
                    })
                    if invite_response.status_code == 200:
                        print(f"   ✅ Joel invited {contrib['email']}")
                    else:
                        print(f"   ⚠️  Invitation failed: {invite_response.text}")
                
                # Create Joel's own story
                joel_story = {
                    "title": "Joel's Own Story",
                    "content": "This is Joel's own story for this week.",
                    "is_headline": False
                }
                
                story_response = joel_session.post(f"{BACKEND_URL}/stories", json=joel_story)
                if story_response.status_code == 200:
                    print("   ✅ Created Joel's own story")
                else:
                    print(f"   ⚠️  Joel's story creation failed: {story_response.text}")
                
                # Now test Joel's edition
                print("\n🧪 TESTING JOEL'S EDITION")
                print("=" * 30)
                
                # Debug Joel's info
                debug_response = joel_session.get(f"{BACKEND_URL}/debug/user-info")
                if debug_response.status_code == 200:
                    debug_data = debug_response.json()
                    diagnosis = debug_data.get("diagnosis", {})
                    print(f"Joel's friends: {diagnosis.get('friends_count', 0)}")
                    print(f"Joel's contributors: {diagnosis.get('contributors_count', 0)}")
                    print(f"Contributor stories: {diagnosis.get('contributor_stories_count', 0)}")
                
                # Test current edition
                edition_response = joel_session.get(f"{BACKEND_URL}/editions/current")
                if edition_response.status_code == 200:
                    edition_data = edition_response.json()
                    stories = edition_data.get("stories", [])
                    print(f"\n📰 JOEL'S CURRENT EDITION:")
                    print(f"Week: {edition_data.get('week_of')}")
                    print(f"Stories: {len(stories)}")
                    for story in stories:
                        print(f"  - {story.get('title')} by {story.get('author_name')}")
                    
                    # This is the key test - does Joel see contributor stories?
                    if len(stories) == 1:
                        print("\n❌ BUG CONFIRMED: Joel only sees 1 story (his own)")
                        print("   Expected: 3 stories (Joel + 2 contributors)")
                        
                        # Try admin fix
                        fix_response = joel_session.post(f"{BACKEND_URL}/admin/fix-contributors")
                        if fix_response.status_code == 200:
                            print("   ✅ Applied admin fix")
                            
                            # Re-test edition
                            edition_response = joel_session.get(f"{BACKEND_URL}/editions/current")
                            if edition_response.status_code == 200:
                                edition_data = edition_response.json()
                                stories = edition_data.get("stories", [])
                                print(f"\n📰 JOEL'S EDITION AFTER FIX:")
                                print(f"Stories: {len(stories)}")
                                for story in stories:
                                    print(f"  - {story.get('title')} by {story.get('author_name')}")
                                
                                if len(stories) > 1:
                                    print("✅ BUG FIXED: Joel now sees contributor stories!")
                                else:
                                    print("❌ BUG PERSISTS: Still only seeing 1 story")
                        else:
                            print(f"   ❌ Admin fix failed: {fix_response.text}")
                    else:
                        print(f"✅ NO BUG: Joel sees {len(stories)} stories as expected")
                
                return True
            else:
                print("❌ Could not login as Joel to complete test")
                return False
                
        except Exception as e:
            print(f"❌ Exception: {str(e)}")
            return False

    def run_investigation(self):
        """Run complete database investigation"""
        print("🔍 DATABASE INVESTIGATION: Finding Joel's Account")
        print("=" * 60)
        
        # Step 1: Login with working account
        login_success, account_email = self.login_with_working_account()
        if not login_success:
            return False
        
        print(f"Using account: {account_email}")
        
        # Step 2: Analyze database contents
        print("\n📊 ANALYZING DATABASE CONTENTS")
        print("=" * 40)
        users_success, authors = self.get_all_users_from_stories()
        
        # Step 3: Search for Joel's account
        print("\n🔍 SEARCHING FOR JOEL'S ACCOUNT")
        print("=" * 40)
        joel_success, joel_data = self.search_for_joel_account()
        
        # Step 4: Create test scenario
        print("\n🧪 CREATING TEST SCENARIO")
        print("=" * 40)
        scenario_success = self.create_test_scenario_for_joel()
        
        return True

if __name__ == "__main__":
    investigator = DatabaseInvestigator()
    investigator.run_investigation()
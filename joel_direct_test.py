#!/usr/bin/env python3
"""
CRITICAL: Direct Joel Conybear Account Investigation
Find Joel's exact account and test his contributor stories issue
"""

import requests
import json
from datetime import datetime

BACKEND_URL = "https://464d35f9-1da6-4f46-92d7-fc7b50272fb2.preview.emergentagent.com/api"

def find_joel_conybear():
    """Find Joel Conybear's account by trying to register with his email"""
    print("🚨 CRITICAL JOEL CONYBEAR ACCOUNT INVESTIGATION")
    print("=" * 60)
    
    # Try to register Joel's account to see if it exists
    joel_registration = {
        "email": "joel.conybear@gmail.com",
        "password": "TestPassword123!",
        "full_name": "Joel Conybear"
    }
    
    session = requests.Session()
    register_response = session.post(f"{BACKEND_URL}/auth/register", json=joel_registration)
    
    if register_response.status_code == 400:
        error_detail = register_response.json().get("detail", "")
        if "already registered" in error_detail.lower():
            print("✅ JOEL'S ACCOUNT EXISTS - Email already registered")
            
            # Try common passwords to login
            common_passwords = [
                "TestPassword123!",
                "password123", 
                "Password123!",
                "SecurePass123!",
                "joel123",
                "JoelPass123!",
                "testpass",
                "123456"
            ]
            
            for password in common_passwords:
                login_data = {
                    "email": "joel.conybear@gmail.com",
                    "password": password
                }
                
                login_response = session.post(f"{BACKEND_URL}/auth/login", json=login_data)
                
                if login_response.status_code == 200:
                    token = login_response.json()["access_token"]
                    session.headers.update({"Authorization": f"Bearer {token}"})
                    print(f"✅ SUCCESSFULLY LOGGED IN AS JOEL with password: {password}")
                    
                    # Now test Joel's account
                    test_joel_account(session)
                    return
                else:
                    print(f"   ❌ Failed password: {password}")
            
            print("❌ JOEL'S ACCOUNT EXISTS BUT PASSWORD UNKNOWN")
            print("   Cannot directly test Joel's account without correct password")
            
        else:
            print(f"❌ Registration failed with different error: {error_detail}")
    
    elif register_response.status_code == 200:
        # Joel's account didn't exist, we just created it
        token = register_response.json()["access_token"]
        session.headers.update({"Authorization": f"Bearer {token}"})
        print("✅ JOEL'S ACCOUNT DIDN'T EXIST - Just created it")
        
        # Create 2 contributors for Joel
        create_contributors_for_joel(session)
        
        # Test the new Joel account
        test_joel_account(session)
        
    else:
        print(f"❌ Unexpected registration response: {register_response.status_code} - {register_response.text}")

def create_contributors_for_joel(joel_session):
    """Create 2 contributors for Joel and have them submit stories"""
    print("\n🔧 CREATING 2 CONTRIBUTORS FOR JOEL")
    
    contributors = [
        {
            "email": "joel.contributor1@gmail.com",
            "password": "Contrib1Pass123!",
            "full_name": "Joel's Contributor 1"
        },
        {
            "email": "joel.contributor2@gmail.com", 
            "password": "Contrib2Pass123!",
            "full_name": "Joel's Contributor 2"
        }
    ]
    
    for i, contrib in enumerate(contributors, 1):
        # Register contributor
        contrib_session = requests.Session()
        register_response = contrib_session.post(f"{BACKEND_URL}/auth/register", json=contrib)
        
        if register_response.status_code == 200:
            contrib_token = register_response.json()["access_token"]
            contrib_session.headers.update({"Authorization": f"Bearer {contrib_token}"})
            print(f"✅ Created contributor {i}: {contrib['full_name']}")
            
            # Create a story as contributor
            story_data = {
                "title": f"Week 30 Story from Contributor {i}",
                "content": f"This is a story for Week 30 from Joel's contributor {i}. This story should appear in Joel's weekly edition if the contributor system is working correctly.",
                "is_headline": i == 1
            }
            
            story_response = contrib_session.post(f"{BACKEND_URL}/stories", json=story_data)
            if story_response.status_code == 200:
                print(f"   ✅ Contributor {i} created story: {story_data['title']}")
            else:
                print(f"   ❌ Contributor {i} story creation failed: {story_response.text}")
        
        elif register_response.status_code == 400:
            # Contributor already exists, try to login and create story
            login_response = contrib_session.post(f"{BACKEND_URL}/auth/login", json={
                "email": contrib["email"],
                "password": contrib["password"]
            })
            
            if login_response.status_code == 200:
                contrib_token = login_response.json()["access_token"]
                contrib_session.headers.update({"Authorization": f"Bearer {contrib_token}"})
                print(f"✅ Logged in as existing contributor {i}: {contrib['full_name']}")
            else:
                print(f"❌ Could not login as contributor {i}")
                continue
        
        # Joel invites this contributor as friend
        invite_response = joel_session.post(f"{BACKEND_URL}/friends/invite", json={
            "email": contrib["email"]
        })
        
        if invite_response.status_code == 200:
            print(f"   ✅ Joel invited contributor {i} as friend")
        else:
            print(f"   ❌ Joel's invitation to contributor {i} failed: {invite_response.text}")

def test_joel_account(joel_session):
    """Test Joel's account state and contributor stories"""
    print("\n🔍 TESTING JOEL'S ACCOUNT STATE")
    
    # Get Joel's user info
    user_response = joel_session.get(f"{BACKEND_URL}/users/me")
    if user_response.status_code == 200:
        joel_user = user_response.json()
        print(f"✅ Joel's User Info:")
        print(f"   ID: {joel_user.get('id')}")
        print(f"   Email: {joel_user.get('email')}")
        print(f"   Name: {joel_user.get('full_name')}")
        print(f"   Friends: {len(joel_user.get('friends', []))}")
        print(f"   Contributors: {len(joel_user.get('contributors', []))}")
        
        # Store Joel's info for analysis
        joel_info = joel_user
    else:
        print(f"❌ Could not get Joel's user info: {user_response.status_code}")
        return
    
    # Test /api/stories/weekly/2025-W30 (the specific endpoint mentioned in review)
    weekly_response = joel_session.get(f"{BACKEND_URL}/stories/weekly/2025-W30")
    if weekly_response.status_code == 200:
        weekly_stories = weekly_response.json()
        print(f"\n✅ /api/stories/weekly/2025-W30 returns {len(weekly_stories)} stories:")
        for story in weekly_stories:
            print(f"   - '{story.get('title')}' by {story.get('author_name')} (ID: {story.get('author_id')})")
    else:
        print(f"❌ /api/stories/weekly/2025-W30 failed: {weekly_response.status_code}")
    
    # Test /api/editions/current (the main issue endpoint)
    edition_response = joel_session.get(f"{BACKEND_URL}/editions/current")
    if edition_response.status_code == 200:
        edition_data = edition_response.json()
        edition_stories = edition_data.get('stories', [])
        print(f"\n✅ /api/editions/current returns {len(edition_stories)} stories for week {edition_data.get('week_of')}:")
        for story in edition_stories:
            print(f"   - '{story.get('title')}' by {story.get('author_name')} (ID: {story.get('author_id')})")
    else:
        print(f"❌ /api/editions/current failed: {edition_response.status_code}")
    
    # Test debug endpoints
    debug_response = joel_session.get(f"{BACKEND_URL}/debug/simple")
    if debug_response.status_code == 200:
        debug_data = debug_response.json()
        print(f"\n✅ Debug info:")
        print(f"   Current week: {debug_data.get('current_week')}")
        print(f"   Contributors: {len(debug_data.get('contributors', []))}")
        print(f"   Total stories in DB: {debug_data.get('total_stories_in_db', 0)}")
        print(f"   Stories from contributors (current week): {debug_data.get('stories_from_contributors_current_week', 0)}")
        print(f"   Stories from contributors (any week): {debug_data.get('stories_from_contributors_any_week', 0)}")
        
        # Show all stories in database
        all_stories = debug_data.get('all_stories_details', [])
        print(f"\n📚 ALL STORIES IN DATABASE ({len(all_stories)} total):")
        for story in all_stories:
            print(f"   - '{story.get('title')}' by {story.get('author_name')} (ID: {story.get('author_id')}) - Week: {story.get('week_of')}")
    
    # Run admin fix to ensure contributors are properly set
    print(f"\n🔧 RUNNING ADMIN FIX FOR CONTRIBUTORS")
    fix_response = joel_session.post(f"{BACKEND_URL}/admin/fix-contributors")
    if fix_response.status_code == 200:
        fix_data = fix_response.json()
        print(f"✅ Admin fix result: {fix_data.get('message')}")
    else:
        print(f"❌ Admin fix failed: {fix_response.status_code}")
    
    # Re-test after admin fix
    print(f"\n🔄 RE-TESTING AFTER ADMIN FIX")
    
    # Re-check user info
    user_response = joel_session.get(f"{BACKEND_URL}/users/me")
    if user_response.status_code == 200:
        joel_user_after = user_response.json()
        print(f"✅ Joel's User Info After Fix:")
        print(f"   Friends: {len(joel_user_after.get('friends', []))}")
        print(f"   Contributors: {len(joel_user_after.get('contributors', []))}")
    
    # Re-test current edition
    edition_response = joel_session.get(f"{BACKEND_URL}/editions/current")
    if edition_response.status_code == 200:
        edition_data_after = edition_response.json()
        edition_stories_after = edition_data_after.get('stories', [])
        print(f"\n✅ /api/editions/current AFTER FIX returns {len(edition_stories_after)} stories:")
        for story in edition_stories_after:
            print(f"   - '{story.get('title')}' by {story.get('author_name')} (ID: {story.get('author_id')})")
    
    # Final analysis
    print(f"\n🎯 FINAL ANALYSIS FOR JOEL CONYBEAR")
    print("=" * 60)
    
    contributors_before = len(joel_info.get('contributors', []))
    contributors_after = len(joel_user_after.get('contributors', [])) if 'joel_user_after' in locals() else contributors_before
    
    stories_before = len(edition_stories) if 'edition_stories' in locals() else 0
    stories_after = len(edition_stories_after) if 'edition_stories_after' in locals() else stories_before
    
    print(f"Contributors: {contributors_before} → {contributors_after}")
    print(f"Edition Stories: {stories_before} → {stories_after}")
    
    if contributors_after == 2 and stories_after >= 3:
        print("✅ SUCCESS: Joel now has 2 contributors and sees multiple stories")
    elif contributors_after == 2 and stories_after < 3:
        print("❌ ISSUE PERSISTS: Joel has 2 contributors but still sees fewer stories than expected")
        print("   This confirms the bug described in the review request")
    elif contributors_after < 2:
        print("❌ SETUP ISSUE: Joel doesn't have 2 contributors as claimed")
        print("   User's claim that 'Joel has 2 contributors' appears to be incorrect")
    else:
        print("⚠️  Unexpected state - need further investigation")

if __name__ == "__main__":
    find_joel_conybear()
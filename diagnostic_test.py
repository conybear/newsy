#!/usr/bin/env python3
"""
Quick diagnostic test to verify the current state of the bidirectional contributor fix
"""

import requests
import json

BACKEND_URL = "https://464d35f9-1da6-4f46-92d7-fc7b50272fb2.preview.emergentagent.com/api"

def test_current_state():
    """Test the current state with existing test credentials"""
    
    # Login as test user
    session = requests.Session()
    login_data = {
        "email": "test@actadiurna.com",
        "password": "TestPass123!"
    }
    
    login_response = session.post(f"{BACKEND_URL}/auth/login", json=login_data)
    
    if login_response.status_code != 200:
        print("❌ Could not login as test user")
        return
    
    token = login_response.json()["access_token"]
    session.headers.update({"Authorization": f"Bearer {token}"})
    
    print("✅ Logged in as test@actadiurna.com")
    
    # Get user info
    user_response = session.get(f"{BACKEND_URL}/users/me")
    if user_response.status_code == 200:
        user_data = user_response.json()
        print(f"✅ User ID: {user_data['id']}")
        print(f"✅ User Name: {user_data['full_name']}")
    
    # Check contributors
    contributors_response = session.get(f"{BACKEND_URL}/contributors/my")
    if contributors_response.status_code == 200:
        contributors = contributors_response.json()
        print(f"✅ User has {len(contributors)} contributors:")
        for contrib in contributors:
            print(f"   - {contrib.get('contributor_name')} ({contrib.get('contributor_email')})")
    else:
        print(f"❌ Could not get contributors: {contributors_response.status_code}")
    
    # Check current newspaper
    newspaper_response = session.get(f"{BACKEND_URL}/newspapers/current")
    if newspaper_response.status_code == 200:
        newspaper = newspaper_response.json()
        stories = newspaper.get("stories", [])
        print(f"✅ Current newspaper has {len(stories)} stories:")
        for story in stories:
            print(f"   - '{story.get('title')}' by {story.get('author_name')}")
    else:
        print(f"❌ Could not get current newspaper: {newspaper_response.status_code}")
    
    # Test missing endpoint
    health_response = session.get(f"{BACKEND_URL}/health")
    if health_response.status_code == 200:
        current_week = health_response.json().get("current_week")
        print(f"✅ Current week: {current_week}")
        
        # Test the missing weekly stories endpoint
        weekly_response = session.get(f"{BACKEND_URL}/stories/weekly/{current_week}")
        if weekly_response.status_code == 404:
            print(f"❌ CONFIRMED: /api/stories/weekly/{current_week} endpoint is MISSING (404)")
        else:
            print(f"✅ Weekly stories endpoint exists: {weekly_response.status_code}")

if __name__ == "__main__":
    print("🔍 DIAGNOSTIC TEST - CURRENT STATE VERIFICATION")
    print("=" * 60)
    test_current_state()
#!/usr/bin/env python3
"""
Debug script to investigate the invitation and contributor system state
"""

import requests
import json

BACKEND_URL = "https://e4f87101-35d9-4339-9777-88089f139507.preview.emergentagent.com/api"

def debug_invitation_system():
    print("🔍 DEBUGGING INVITATION AND CONTRIBUTOR SYSTEM")
    print("=" * 60)
    
    # Login as both users
    session_a = requests.Session()
    session_b = requests.Session()
    
    # User A login
    login_a = session_a.post(f"{BACKEND_URL}/auth/login", json={
        "email": "test@actadiurna.com",
        "password": "TestPass123!"
    })
    
    if login_a.status_code == 200:
        token_a = login_a.json()["access_token"]
        session_a.headers.update({"Authorization": f"Bearer {token_a}"})
        print("✅ User A logged in successfully")
    else:
        print(f"❌ User A login failed: {login_a.status_code}")
        return
    
    # User B login
    login_b = session_b.post(f"{BACKEND_URL}/auth/login", json={
        "email": "contributor@actadiurna.com", 
        "password": "ContribPass123!"
    })
    
    if login_b.status_code == 200:
        token_b = login_b.json()["access_token"]
        session_b.headers.update({"Authorization": f"Bearer {token_b}"})
        print("✅ User B logged in successfully")
    else:
        print(f"❌ User B login failed: {login_b.status_code}")
        return
    
    # Get user data
    user_a_data = session_a.get(f"{BACKEND_URL}/users/me").json()
    user_b_data = session_b.get(f"{BACKEND_URL}/users/me").json()
    
    print(f"\n👤 User A: {user_a_data['full_name']} (ID: {user_a_data['id']})")
    print(f"👤 User B: {user_b_data['full_name']} (ID: {user_b_data['id']})")
    
    # Check sent invitations from User A
    print(f"\n📤 SENT INVITATIONS FROM USER A:")
    sent_invitations = session_a.get(f"{BACKEND_URL}/invitations/sent").json()
    print(f"   Found {len(sent_invitations)} sent invitations")
    for inv in sent_invitations:
        print(f"   - To: {inv['to_email']}, Status: {inv['status']}, ID: {inv['id']}")
    
    # Check received invitations for User B
    print(f"\n📥 RECEIVED INVITATIONS FOR USER B:")
    received_invitations = session_b.get(f"{BACKEND_URL}/invitations/received").json()
    print(f"   Found {len(received_invitations)} received invitations")
    for inv in received_invitations:
        print(f"   - From: {inv['from_user_email']}, Status: {inv['status']}, ID: {inv['id']}")
    
    # Check current contributors for both users
    print(f"\n🤝 CURRENT CONTRIBUTORS:")
    contributors_a = session_a.get(f"{BACKEND_URL}/contributors/my").json()
    contributors_b = session_b.get(f"{BACKEND_URL}/contributors/my").json()
    
    print(f"   User A has {len(contributors_a)} contributors:")
    for contrib in contributors_a:
        print(f"   - {contrib['contributor_name']} ({contrib['contributor_id']})")
    
    print(f"   User B has {len(contributors_b)} contributors:")
    for contrib in contributors_b:
        print(f"   - {contrib['contributor_name']} ({contrib['contributor_id']})")
    
    # Try to add contributor if there's a received invitation
    if received_invitations:
        print(f"\n🔧 ATTEMPTING TO ADD CONTRIBUTOR:")
        invitation_id = received_invitations[0]["id"]
        add_response = session_b.post(f"{BACKEND_URL}/contributors/add", json={"invitation_id": invitation_id})
        
        print(f"   Status: {add_response.status_code}")
        if add_response.status_code == 200:
            result = add_response.json()
            print(f"   Response: {result}")
        else:
            print(f"   Error: {add_response.text}")
        
        # Re-check contributors after attempt
        print(f"\n🔄 CONTRIBUTORS AFTER ADD ATTEMPT:")
        contributors_a_after = session_a.get(f"{BACKEND_URL}/contributors/my").json()
        contributors_b_after = session_b.get(f"{BACKEND_URL}/contributors/my").json()
        
        print(f"   User A now has {len(contributors_a_after)} contributors:")
        for contrib in contributors_a_after:
            print(f"   - {contrib['contributor_name']} ({contrib['contributor_id']})")
        
        print(f"   User B now has {len(contributors_b_after)} contributors:")
        for contrib in contributors_b_after:
            print(f"   - {contrib['contributor_name']} ({contrib['contributor_id']})")
    
    # Test weekly stories to see current aggregation
    print(f"\n📰 WEEKLY STORIES AGGREGATION TEST:")
    health_response = session_a.get(f"{BACKEND_URL}/health")
    current_week = health_response.json()["current_week"]
    
    stories_a = session_a.get(f"{BACKEND_URL}/stories/weekly/{current_week}").json()
    stories_b = session_b.get(f"{BACKEND_URL}/stories/weekly/{current_week}").json()
    
    print(f"   Current week: {current_week}")
    print(f"   User A sees {len(stories_a)} stories:")
    for story in stories_a:
        print(f"   - '{story['title']}' by {story['author_name']}")
    
    print(f"   User B sees {len(stories_b)} stories:")
    for story in stories_b:
        print(f"   - '{story['title']}' by {story['author_name']}")

if __name__ == "__main__":
    debug_invitation_system()
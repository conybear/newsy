#!/usr/bin/env python3
"""
Debug newspaper generation specifically
"""

import requests
import json

BACKEND_URL = "https://464d35f9-1da6-4f46-92d7-fc7b50272fb2.preview.emergentagent.com/api"

def debug_newspaper_generation():
    print("🗞️ DEBUGGING NEWSPAPER GENERATION")
    print("=" * 50)
    
    # Login as both users
    session_a = requests.Session()
    session_b = requests.Session()
    
    # User A login
    login_a = session_a.post(f"{BACKEND_URL}/auth/login", json={
        "email": "test@actadiurna.com",
        "password": "TestPass123!"
    })
    token_a = login_a.json()["access_token"]
    session_a.headers.update({"Authorization": f"Bearer {token_a}"})
    
    # User B login
    login_b = session_b.post(f"{BACKEND_URL}/auth/login", json={
        "email": "contributor@actadiurna.com", 
        "password": "ContribPass123!"
    })
    token_b = login_b.json()["access_token"]
    session_b.headers.update({"Authorization": f"Bearer {token_b}"})
    
    # Get current week
    health_response = session_a.get(f"{BACKEND_URL}/health")
    current_week = health_response.json()["current_week"]
    print(f"Current week: {current_week}")
    
    # Test newspaper generation for both users
    print(f"\n📰 TESTING NEWSPAPER GENERATION:")
    
    # User A's newspaper
    newspaper_a_response = session_a.get(f"{BACKEND_URL}/newspapers/current")
    if newspaper_a_response.status_code == 200:
        newspaper_a = newspaper_a_response.json()
        stories_a = newspaper_a.get("stories", [])
        print(f"\n👤 User A's newspaper:")
        print(f"   Week: {newspaper_a.get('week_of')}")
        print(f"   Title: {newspaper_a.get('title')}")
        print(f"   Stories: {len(stories_a)}")
        for story in stories_a:
            print(f"   - '{story['title']}' by {story['author_name']} (ID: {story['author_id']})")
    else:
        print(f"❌ User A newspaper error: {newspaper_a_response.status_code}")
    
    # User B's newspaper
    newspaper_b_response = session_b.get(f"{BACKEND_URL}/newspapers/current")
    if newspaper_b_response.status_code == 200:
        newspaper_b = newspaper_b_response.json()
        stories_b = newspaper_b.get("stories", [])
        print(f"\n👤 User B's newspaper:")
        print(f"   Week: {newspaper_b.get('week_of')}")
        print(f"   Title: {newspaper_b.get('title')}")
        print(f"   Stories: {len(stories_b)}")
        for story in stories_b:
            print(f"   - '{story['title']}' by {story['author_name']} (ID: {story['author_id']})")
    else:
        print(f"❌ User B newspaper error: {newspaper_b_response.status_code}")
    
    # Force regenerate newspapers to test fresh generation
    print(f"\n🔄 FORCE REGENERATING NEWSPAPERS:")
    
    regen_a_response = session_a.post(f"{BACKEND_URL}/newspapers/regenerate")
    if regen_a_response.status_code == 200:
        regen_a_data = regen_a_response.json()
        new_newspaper_a = regen_a_data.get("newspaper", {})
        new_stories_a = new_newspaper_a.get("stories", [])
        print(f"\n👤 User A's regenerated newspaper:")
        print(f"   Stories: {len(new_stories_a)}")
        for story in new_stories_a:
            print(f"   - '{story['title']}' by {story['author_name']} (ID: {story['author_id']})")
    else:
        print(f"❌ User A regenerate error: {regen_a_response.status_code}")
    
    regen_b_response = session_b.post(f"{BACKEND_URL}/newspapers/regenerate")
    if regen_b_response.status_code == 200:
        regen_b_data = regen_b_response.json()
        new_newspaper_b = regen_b_data.get("newspaper", {})
        new_stories_b = new_newspaper_b.get("stories", [])
        print(f"\n👤 User B's regenerated newspaper:")
        print(f"   Stories: {len(new_stories_b)}")
        for story in new_stories_b:
            print(f"   - '{story['title']}' by {story['author_name']} (ID: {story['author_id']})")
    else:
        print(f"❌ User B regenerate error: {regen_b_response.status_code}")

if __name__ == "__main__":
    debug_newspaper_generation()
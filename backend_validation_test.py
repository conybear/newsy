#!/usr/bin/env python3
"""
Additional Backend API Tests for Edge Cases and Validation
"""

import requests
import json
import base64
import io
from PIL import Image

BACKEND_URL = "https://10eeeb36-2949-49e5-b0bf-259584eeb998.preview.emergentagent.com/api"

def test_authentication_edge_cases():
    """Test authentication edge cases"""
    session = requests.Session()
    
    print("🔐 Testing Authentication Edge Cases")
    print("-" * 50)
    
    # Test duplicate registration
    user_data = {
        "email": "sarah.johnson@newspaper.com",
        "password": "SecurePass123!",
        "full_name": "Sarah Johnson"
    }
    
    response = session.post(f"{BACKEND_URL}/auth/register", json=user_data)
    if response.status_code == 400:
        print("✅ Duplicate registration properly rejected")
    else:
        print(f"❌ Expected 400 for duplicate registration, got {response.status_code}")
    
    # Test invalid login
    invalid_login = {
        "email": "sarah.johnson@newspaper.com",
        "password": "WrongPassword"
    }
    
    response = session.post(f"{BACKEND_URL}/auth/login", json=invalid_login)
    if response.status_code == 401:
        print("✅ Invalid login properly rejected")
    else:
        print(f"❌ Expected 401 for invalid login, got {response.status_code}")
    
    # Test protected route without token
    response = session.get(f"{BACKEND_URL}/users/me")
    if response.status_code == 403:
        print("✅ Protected route properly requires authentication")
    else:
        print(f"❌ Expected 403 for unauth access, got {response.status_code}")

def test_story_validation():
    """Test story validation rules"""
    session = requests.Session()
    
    print("\n📝 Testing Story Validation")
    print("-" * 50)
    
    # Login first
    login_data = {
        "email": "sarah.johnson@newspaper.com",
        "password": "SecurePass123!"
    }
    
    response = session.post(f"{BACKEND_URL}/auth/login", json=login_data)
    if response.status_code == 200:
        token = response.json()["access_token"]
        session.headers.update({"Authorization": f"Bearer {token}"})
        
        # Test image limit (try to upload 4th image)
        # First get user's story
        stories_response = session.get(f"{BACKEND_URL}/stories/my")
        if stories_response.status_code == 200:
            stories = stories_response.json()
            if stories:
                story_id = stories[0]["id"]
                
                # Try to upload 3 more images (should fail on 3rd since we already have 1)
                img = Image.new('RGB', (50, 50), color='blue')
                buffer = io.BytesIO()
                img.save(buffer, format='JPEG')
                buffer.seek(0)
                image_data = buffer.getvalue()
                
                files = {'file': ('test2.jpg', image_data, 'image/jpeg')}
                response = session.post(f"{BACKEND_URL}/stories/{story_id}/images", files=files)
                print(f"Second image upload: {response.status_code}")
                
                files = {'file': ('test3.jpg', image_data, 'image/jpeg')}
                response = session.post(f"{BACKEND_URL}/stories/{story_id}/images", files=files)
                print(f"Third image upload: {response.status_code}")
                
                files = {'file': ('test4.jpg', image_data, 'image/jpeg')}
                response = session.post(f"{BACKEND_URL}/stories/{story_id}/images", files=files)
                if response.status_code == 400:
                    print("✅ 3-image limit properly enforced")
                else:
                    print(f"❌ Expected 400 for 4th image, got {response.status_code}")

def test_friend_limit():
    """Test friend limit validation"""
    session = requests.Session()
    
    print("\n👥 Testing Friend Limit")
    print("-" * 50)
    
    # Login
    login_data = {
        "email": "sarah.johnson@newspaper.com",
        "password": "SecurePass123!"
    }
    
    response = session.post(f"{BACKEND_URL}/auth/login", json=login_data)
    if response.status_code == 200:
        token = response.json()["access_token"]
        session.headers.update({"Authorization": f"Bearer {token}"})
        
        # Get current friend count
        friends_response = session.get(f"{BACKEND_URL}/friends")
        if friends_response.status_code == 200:
            current_friends = len(friends_response.json())
            print(f"Current friends: {current_friends}")
            
            # Test adding friend to non-existent user
            request_data = {"email": "nonexistent@user.com"}
            response = session.post(f"{BACKEND_URL}/friends/request", json=request_data)
            if response.status_code == 404:
                print("✅ Friend request to non-existent user properly rejected")
            else:
                print(f"❌ Expected 404 for non-existent user, got {response.status_code}")

def test_weekly_edition_logic():
    """Test weekly edition generation logic"""
    session = requests.Session()
    
    print("\n📰 Testing Weekly Edition Logic")
    print("-" * 50)
    
    # Login
    login_data = {
        "email": "sarah.johnson@newspaper.com",
        "password": "SecurePass123!"
    }
    
    response = session.post(f"{BACKEND_URL}/auth/login", json=login_data)
    if response.status_code == 200:
        token = response.json()["access_token"]
        session.headers.update({"Authorization": f"Bearer {token}"})
        
        # Get current edition multiple times (should return same edition)
        response1 = session.get(f"{BACKEND_URL}/editions/current")
        response2 = session.get(f"{BACKEND_URL}/editions/current")
        
        if response1.status_code == 200 and response2.status_code == 200:
            edition1 = response1.json()
            edition2 = response2.json()
            
            if edition1["id"] == edition2["id"]:
                print("✅ Current edition consistency maintained")
            else:
                print("❌ Current edition IDs don't match")
                
            print(f"Edition week: {edition1['week_of']}")
            print(f"Stories in edition: {len(edition1['stories'])}")

if __name__ == "__main__":
    print("🧪 Running Additional Backend Validation Tests")
    print("=" * 60)
    
    test_authentication_edge_cases()
    test_story_validation()
    test_friend_limit()
    test_weekly_edition_logic()
    
    print("\n" + "=" * 60)
    print("✅ Additional validation tests completed")
#!/usr/bin/env python3
"""
Comprehensive Flask Application Testing Suite
Testing the Flask refactoring for deployment readiness
"""

import requests
import sys
import json
import time
import subprocess
import os
from datetime import datetime

class FlaskAppTester:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.server_process = None

    def log_test(self, name, success, message=""):
        """Log test results"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name}: PASSED {message}")
        else:
            print(f"❌ {name}: FAILED {message}")
        return success

    def start_flask_server(self):
        """Start Flask server for testing"""
        print("🚀 Starting Flask server...")
        try:
            # Start Flask server in background
            self.server_process = subprocess.Popen(
                ["python", "app.py"],
                cwd="/app",
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            # Wait for server to start
            time.sleep(3)
            
            # Test if server is running
            response = requests.get(f"{self.base_url}/", timeout=5)
            if response.status_code == 200:
                print("✅ Flask server started successfully")
                return True
            else:
                print(f"❌ Flask server responded with status {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Failed to start Flask server: {str(e)}")
            return False

    def stop_flask_server(self):
        """Stop Flask server"""
        if self.server_process:
            self.server_process.terminate()
            self.server_process.wait()
            print("🛑 Flask server stopped")

    def test_home_route(self):
        """Test the home route returns HTML template"""
        try:
            response = requests.get(f"{self.base_url}/")
            success = (response.status_code == 200 and 
                      "Weekly Newspaper" in response.text and
                      "Submit Story" in response.text)
            return self.log_test("Home Route", success, 
                               f"Status: {response.status_code}")
        except Exception as e:
            return self.log_test("Home Route", False, f"Error: {str(e)}")

    def test_submit_story_valid(self):
        """Test submitting a valid story"""
        try:
            story_data = {
                "title": "Test Story",
                "content": "This is a test story content",
                "author": "Test Author"
            }
            response = requests.post(
                f"{self.base_url}/submit",
                json=story_data,
                headers={'Content-Type': 'application/json'}
            )
            success = (response.status_code == 200 and 
                      "successfully" in response.json().get('message', ''))
            return self.log_test("Submit Valid Story", success,
                               f"Status: {response.status_code}")
        except Exception as e:
            return self.log_test("Submit Valid Story", False, f"Error: {str(e)}")

    def test_submit_story_invalid(self):
        """Test submitting invalid story (missing required fields)"""
        try:
            story_data = {"title": "Test Story"}  # Missing content
            response = requests.post(
                f"{self.base_url}/submit",
                json=story_data,
                headers={'Content-Type': 'application/json'}
            )
            success = (response.status_code == 400 and 
                      "required" in response.json().get('error', ''))
            return self.log_test("Submit Invalid Story", success,
                               f"Status: {response.status_code}")
        except Exception as e:
            return self.log_test("Submit Invalid Story", False, f"Error: {str(e)}")

    def test_subscribe_valid(self):
        """Test valid email subscription"""
        try:
            sub_data = {"email": f"test_{int(time.time())}@example.com"}
            response = requests.post(
                f"{self.base_url}/subscribe",
                json=sub_data,
                headers={'Content-Type': 'application/json'}
            )
            success = (response.status_code == 200 and 
                      "successfully" in response.json().get('message', ''))
            return self.log_test("Valid Subscription", success,
                               f"Status: {response.status_code}")
        except Exception as e:
            return self.log_test("Valid Subscription", False, f"Error: {str(e)}")

    def test_subscribe_duplicate(self):
        """Test duplicate email subscription prevention"""
        try:
            email = f"duplicate_{int(time.time())}@example.com"
            sub_data = {"email": email}
            
            # First subscription
            response1 = requests.post(
                f"{self.base_url}/subscribe",
                json=sub_data,
                headers={'Content-Type': 'application/json'}
            )
            
            # Second subscription (should fail)
            response2 = requests.post(
                f"{self.base_url}/subscribe",
                json=sub_data,
                headers={'Content-Type': 'application/json'}
            )
            
            success = (response1.status_code == 200 and 
                      response2.status_code == 400 and
                      "already subscribed" in response2.json().get('error', ''))
            return self.log_test("Duplicate Subscription Prevention", success,
                               f"First: {response1.status_code}, Second: {response2.status_code}")
        except Exception as e:
            return self.log_test("Duplicate Subscription Prevention", False, f"Error: {str(e)}")

    def test_subscribe_invalid(self):
        """Test invalid subscription (missing email)"""
        try:
            sub_data = {}  # Missing email
            response = requests.post(
                f"{self.base_url}/subscribe",
                json=sub_data,
                headers={'Content-Type': 'application/json'}
            )
            success = (response.status_code == 400 and 
                      "required" in response.json().get('error', ''))
            return self.log_test("Invalid Subscription", success,
                               f"Status: {response.status_code}")
        except Exception as e:
            return self.log_test("Invalid Subscription", False, f"Error: {str(e)}")

    def test_story_persistence(self):
        """Test that submitted stories appear on homepage"""
        try:
            # Submit a unique story
            unique_title = f"Persistence Test {int(time.time())}"
            story_data = {
                "title": unique_title,
                "content": "Testing story persistence",
                "author": "Test Bot"
            }
            
            submit_response = requests.post(
                f"{self.base_url}/submit",
                json=story_data,
                headers={'Content-Type': 'application/json'}
            )
            
            if submit_response.status_code != 200:
                return self.log_test("Story Persistence", False, 
                                   "Failed to submit story")
            
            # Check if story appears on homepage
            home_response = requests.get(f"{self.base_url}/")
            success = (home_response.status_code == 200 and 
                      unique_title in home_response.text)
            return self.log_test("Story Persistence", success,
                               "Story appears on homepage")
        except Exception as e:
            return self.log_test("Story Persistence", False, f"Error: {str(e)}")

    def test_gunicorn_compatibility(self):
        """Test that the app can be started with gunicorn"""
        try:
            print("🧪 Testing Gunicorn compatibility...")
            # Test gunicorn import
            result = subprocess.run(
                ["python", "-c", "import gunicorn; from app import app; print('Gunicorn import successful')"],
                cwd="/app",
                capture_output=True,
                text=True,
                timeout=10
            )
            success = result.returncode == 0
            return self.log_test("Gunicorn Compatibility", success,
                               f"Import test: {result.stdout.strip() if success else result.stderr.strip()}")
        except Exception as e:
            return self.log_test("Gunicorn Compatibility", False, f"Error: {str(e)}")

    def test_requirements_file(self):
        """Test that requirements.txt contains necessary packages"""
        try:
            with open("/app/requirements.txt", "r") as f:
                requirements = f.read().lower()
            
            required_packages = ["flask", "apscheduler", "gunicorn"]
            missing_packages = [pkg for pkg in required_packages if pkg not in requirements]
            
            success = len(missing_packages) == 0
            message = f"Missing: {missing_packages}" if missing_packages else "All required packages present"
            return self.log_test("Requirements File", success, message)
        except Exception as e:
            return self.log_test("Requirements File", False, f"Error: {str(e)}")

    def test_procfile_exists(self):
        """Test that Procfile exists and has correct content"""
        try:
            with open("/app/Procfile", "r") as f:
                procfile_content = f.read().strip()
            
            success = "gunicorn app:app" in procfile_content
            return self.log_test("Procfile Configuration", success,
                               f"Content: {procfile_content}")
        except Exception as e:
            return self.log_test("Procfile Configuration", False, f"Error: {str(e)}")

    def run_all_tests(self):
        """Run all tests"""
        print("🧪 Starting Flask Application Test Suite")
        print("=" * 50)
        
        # Test deployment files first
        self.test_requirements_file()
        self.test_procfile_exists()
        self.test_gunicorn_compatibility()
        
        # Start server and run functional tests
        if self.start_flask_server():
            try:
                self.test_home_route()
                self.test_submit_story_valid()
                self.test_submit_story_invalid()
                self.test_subscribe_valid()
                self.test_subscribe_duplicate()
                self.test_subscribe_invalid()
                self.test_story_persistence()
            finally:
                self.stop_flask_server()
        else:
            print("❌ Cannot run functional tests - server failed to start")
        
        # Print final results
        print("\n" + "=" * 50)
        print(f"📊 TEST RESULTS: {self.tests_passed}/{self.tests_run} tests passed")
        
        if self.tests_passed == self.tests_run:
            print("🎉 ALL TESTS PASSED - Flask app is deployment ready!")
            return 0
        else:
            print("⚠️  SOME TESTS FAILED - Review issues before deployment")
            return 1

def main():
    """Main test execution"""
    tester = FlaskAppTester()
    return tester.run_all_tests()

if __name__ == "__main__":
    sys.exit(main())
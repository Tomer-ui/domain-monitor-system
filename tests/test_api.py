#!/usr/bin/env python3
"""
API Tests for Domain Monitor System
Tests backend endpoints to ensure they work correctly
"""

import requests
import sys
import time

# Configuration - YOUR app runs on port 8080
BASE_URL = "http://localhost:8080"
TEST_USER = f"jenkins_test_{int(time.time())}"  # Unique username each run
TEST_PASSWORD = "TestPass123!"

def wait_for_app():
    """Wait for the app to be ready"""
    print("⏳ Waiting for Domain Monitor to be ready...")
    for i in range(30):
        try:
            response = requests.get(f"{BASE_URL}/", timeout=2)
            if response.status_code in [200, 302]:
                print("✓ Domain Monitor is ready!")
                return True
        except requests.exceptions.RequestException:
            time.sleep(1)
            if i % 5 == 0 and i > 0:
                print(f"   Still waiting... ({i}/30 seconds)")
    
    print("✗ Domain Monitor failed to start")
    return False


def test_health_check():
    """Test if the domain monitor is running"""
    print("\n--- Test 1: Health Check ---")
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        assert response.status_code in [200, 302], f"Unexpected status: {response.status_code}"
        print(f"✓ Health check passed (Status: {response.status_code})")
        return True
    except Exception as e:
        print(f"✗ Health check failed: {e}")
        return False


def test_register():
    """Test user registration"""
    print("\n--- Test 2: User Registration ---")
    try:
        payload = {
            "username": TEST_USER,
            "password": TEST_PASSWORD
        }
        
        response = requests.post(
            f"{BASE_URL}/api/register",  # ✅ Correct endpoint
            json=payload,
            timeout=10
        )
        
        # 201 = created, 409 = already exists (both acceptable)
        assert response.status_code in [201, 409], \
            f"Registration failed: {response.status_code} - {response.text}"
        
        data = response.json()
        print(f"✓ Registration test passed: {data.get('message')}")
        return True
    except Exception as e:
        print(f"✗ Registration test failed: {e}")
        return False


def test_login():
    """Test user login"""
    print("\n--- Test 3: User Login ---")
    try:
        payload = {
            "username": TEST_USER,
            "password": TEST_PASSWORD
        }
        
        # Create session to maintain cookies (Flask uses sessions)
        session = requests.Session()
        
        response = session.post(
            f"{BASE_URL}/api/login",
            json=payload,
            timeout=10
        )
        
        assert response.status_code == 200, \
            f"Login failed: {response.status_code} - {response.text}"
        
        data = response.json()
        print(f"✓ Login test passed: {data.get('message')}")
        
        return session  # Return session with login cookie
    except Exception as e:
        print(f"✗ Login test failed: {e}")
        return None


def test_add_domain(session):
    """Test adding a single domain"""
    print("\n--- Test 4: Add Domain ---")
    try:
        payload = {
            "domain": "google.com"
        }
        
        response = session.post(
            f"{BASE_URL}/api/add_domain",  # ✅ Correct endpoint
            json=payload,
            timeout=10
        )
        
        # 201 = created, 409 = already exists
        assert response.status_code in [201, 409], \
            f"Add domain failed: {response.status_code} - {response.text}"
        
        data = response.json()
        print(f"✓ Add domain test passed: {data.get('message')}")
        return True
    except Exception as e:
        print(f"✗ Add domain test failed: {e}")
        return False


def test_get_domains(session):
    """Test getting user's domains list"""
    print("\n--- Test 5: Get Domains ---")
    try:
        response = session.get(
            f"{BASE_URL}/api/domains",  # ✅ Correct - GET method
            timeout=20  # Domain checks can take time
        )
        
        assert response.status_code == 200, \
            f"Get domains failed: {response.status_code} - {response.text}"
        
        data = response.json()
        assert isinstance(data, list), "Response should be a list"
        
        print(f"✓ Get domains test passed (Found {len(data)} domains)")
        if len(data) > 0:
            domain = data[0]
            print(f"   Example: {domain.get('domain')} - {domain.get('status')}")
        
        return True
    except Exception as e:
        print(f"✗ Get domains test failed: {e}")
        return False


def test_remove_domain(session):
    """Test removing a domain"""
    print("\n--- Test 6: Remove Domain ---")
    try:
        payload = {
            "domain": "google.com"
        }
        
        response = session.post(
            f"{BASE_URL}/api/remove_domain",  # ✅ Correct endpoint
            json=payload,
            timeout=10
        )
        
        # 200 = removed, 404 = not found
        assert response.status_code in [200, 404], \
            f"Remove domain failed: {response.status_code} - {response.text}"
        
        data = response.json()
        print(f"✓ Remove domain test passed: {data.get('message')}")
        return True
    except Exception as e:
        print(f"✗ Remove domain test failed: {e}")
        return False


def test_bulk_upload(session):
    """Test bulk domain upload"""
    print("\n--- Test 7: Bulk Upload ---")
    try:
        import tempfile
        import os
        
        # Create temporary file with domains
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write("example.com\n")
            f.write("github.com\n")
            f.write("stackoverflow.com\n")
            temp_file = f.name
        
        # Upload file
        with open(temp_file, 'rb') as f:
            files = {'file': ('domains.txt', f, 'text/plain')}
            response = session.post(
                f"{BASE_URL}/api/bulk_upload",
                files=files,
                timeout=15
            )
        
        # Cleanup
        os.unlink(temp_file)
        
        assert response.status_code == 200, \
            f"Bulk upload failed: {response.status_code} - {response.text}"
        
        data = response.json()
        print(f"✓ Bulk upload test passed: {data.get('message')}")
        return True
    except Exception as e:
        print(f"✗ Bulk upload test failed: {e}")
        return False


def test_logout(session):
    """Test logout"""
    print("\n--- Test 8: Logout ---")
    try:
        response = session.post(
            f"{BASE_URL}/api/logout",
            timeout=5
        )
        
        assert response.status_code == 200, \
            f"Logout failed: {response.status_code}"
        
        data = response.json()
        print(f"✓ Logout test passed: {data.get('message')}")
        return True
    except Exception as e:
        print(f"✗ Logout test failed: {e}")
        return False


def test_session_check(session):
    """Test session verification"""
    print("\n--- Test 9: Session Check ---")
    try:
        # Before logout - should be logged in
        response = session.get(
            f"{BASE_URL}/api/session",
            timeout=5
        )
        
        assert response.status_code == 200, \
            f"Session check failed: {response.status_code}"
        
        data = response.json()
        assert data.get('loggedIn') == True, "User should be logged in"
        
        print(f"✓ Session check passed (User: {data.get('username')})")
        return True
    except Exception as e:
        print(f"✗ Session check failed: {e}")
        return False


def run_all_tests():
    """Run all API tests"""
    print("=" * 70)
    print("🧪 DOMAIN MONITOR SYSTEM - API TESTS")
    print("=" * 70)
    
    # Wait for app to be ready
    if not wait_for_app():
        print("\n❌ FAILED: Domain Monitor didn't start")
        print("\n💡 Troubleshooting:")
        print("   1. Is your app running? Check: curl http://localhost:8080")
        print("   2. Check app logs for errors")
        print("   3. Verify port 8080 is not blocked")
        sys.exit(1)
    
    # Run tests
    results = []
    
    # Test 1: Health check
    results.append(test_health_check())
    
    # Test 2: Registration
    results.append(test_register())
    
    # Test 3: Login (returns session for subsequent tests)
    session = test_login()
    if session:
        results.append(True)  # Login passed
        
        # Test 4: Add domain
        results.append(test_add_domain(session))
        
        # Test 5: Get domains
        results.append(test_get_domains(session))
        
        # Test 6: Bulk upload
        results.append(test_bulk_upload(session))
        
        # Test 7: Session check
        results.append(test_session_check(session))
        
        # Test 8: Remove domain
        results.append(test_remove_domain(session))
        
        # Test 9: Logout
        results.append(test_logout(session))
    else:
        results.append(False)  # Login failed
        print("\n⚠️  Skipping remaining tests due to login failure")
        results.extend([False] * 6)  # Mark remaining tests as failed
    
    # Summary
    print("\n" + "=" * 70)
    passed = sum(results)
    total = len(results)
    print(f"📊 TEST RESULTS: {passed}/{total} PASSED")
    print("=" * 70)
    
    if all(results):
        print("\n🎉 ALL API TESTS PASSED!")
        sys.exit(0)
    else:
        print("\n❌ SOME API TESTS FAILED!")
        print("Review the output above for details.")
        sys.exit(1)


if __name__ == "__main__":
    run_all_tests()

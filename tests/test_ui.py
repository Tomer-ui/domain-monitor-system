#!/usr/bin/env python3
"""
UI Tests for Domain Monitor System
Tests the web interface using Selenium
"""
import os
import sys
import time
import tempfile
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service


# Configuration
APP_URL = "http://127.0.0.1:8080"
TEST_USER = f"selenium_test_{int(time.time())}"
TEST_PASSWORD = "TestPass123!"

def setup_driver():
    """Setup Chrome browser for testing"""
    print("Setting up Chrome browser...")
    
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # No GUI
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    
    try:
        # Try to use system chromedriver
        driver = webdriver.Chrome(options=chrome_options)
        print("✓ Chrome browser ready")
        return driver
    except Exception as e:
        print(f"✗ Failed to setup browser: {e}")
        sys.exit(1)


def wait_for_app(driver, max_attempts=30):
    """Wait for domain monitor to load"""
    print("\n⏳ Waiting for Domain Monitor UI to load...")
    
    for attempt in range(max_attempts):
        try:
            driver.get(APP_URL)
            # Wait for body tag to exist
            WebDriverWait(driver, 2).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            print("✓ Domain Monitor UI loaded")
            return True
        except:
            time.sleep(1)
            if attempt % 5 == 0:
                print(f"   Still waiting... ({attempt}/{max_attempts})")
    
    print("✗ Failed to load UI")
    return False


def test_register_flow(driver):
    """Test 1: User can register"""
    print("\n--- Test 1: User Registration Flow ---")
    try:
        # Navigate to register page
        driver.get(f"{APP_URL}/register")
        
        # Wait for register form to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "registerForm"))
        )
        
        # Find and fill username field
        username_field = driver.find_element(By.ID, "username")
        username_field.clear()
        username_field.send_keys(TEST_USER)
        
        # Find and fill password field
        password_field = driver.find_element(By.ID, "password")
        password_field.clear()
        password_field.send_keys(TEST_PASSWORD)
        
        # Click submit button
        submit_button = driver.find_element(By.CSS_SELECTOR, "button.form__button")
        submit_button.click()
        
        # Wait for redirect or success message
        time.sleep(3)
        
        # Check if we're redirected to login page
        current_url = driver.current_url
        assert "login" in current_url or "Login successful" in driver.page_source, \
            f"Registration didn't work properly. Current URL: {current_url}"
        
        print("✓ Registration flow passed")
        return True
        
    except Exception as e:
        print(f"✗ Registration flow failed: {e}")
        driver.save_screenshot("/tmp/register_failed.png")
        return False


def test_login_flow(driver):
    """Test 2: User can login"""
    print("\n--- Test 2: Login Flow ---")
    try:
        # Navigate to login page
        driver.get(f"{APP_URL}/login")
        
        # Wait for login form
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "loginForm"))
        )
        
        # Fill username
        username_field = driver.find_element(By.ID, "username")
        username_field.clear()
        username_field.send_keys(TEST_USER)
        
        # Fill password
        password_field = driver.find_element(By.ID, "password")
        password_field.clear()
        password_field.send_keys(TEST_PASSWORD)
        
        # Click submit
        submit_button = driver.find_element(By.CSS_SELECTOR, "button.form__button")
        submit_button.click()
        
        # Wait for redirect to dashboard
        WebDriverWait(driver, 10).until(
            lambda d: "dashboard" in d.current_url
        )
        
        print("✓ Login flow passed")
        return True
        
    except Exception as e:
        print(f"✗ Login flow failed: {e}")
        driver.save_screenshot("/tmp/login_failed.png")
        return False


def test_add_single_domain(driver):
    """Test 3: User can add a single domain"""
    print("\n--- Test 3: Add Single Domain ---")
    try:
        # Should already be on dashboard from login test
        if "dashboard" not in driver.current_url:
            driver.get(f"{APP_URL}/dashboard")
            time.sleep(2)
        
        # Wait for add domain form
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "addDomainForm"))
        )
        
        # Find domain input field
        domain_input = driver.find_element(By.CSS_SELECTOR, "#addDomainForm input[name='domain']")
        domain_input.clear()
        domain_input.send_keys("google.com")
        
        # Find and click submit button
        submit_button = driver.find_element(By.CSS_SELECTOR, "#addDomainForm button[type='submit']")
        submit_button.click()
        
        # Wait for domain to appear in table
        time.sleep(3)  # Give time for domain check
        
        # Check if table has rows
        table_body = driver.find_element(By.CSS_SELECTOR, "#domainsTable tbody")
        rows = table_body.find_elements(By.TAG_NAME, "tr")
        
        assert len(rows) > 0, "No domains found in table after adding"
        
        # Check if google.com is in the table
        table_text = table_body.text
        assert "google.com" in table_text, "Added domain not found in table"
        
        print("✓ Add single domain passed")
        return True
        
    except Exception as e:
        print(f"✗ Add single domain failed: {e}")
        driver.save_screenshot("/tmp/add_domain_failed.png")
        return False


def test_domain_results(driver):
    """Test 4: Domain results are displayed"""
    print("\n--- Test 4: Domain Results Display ---")
    try:
        # Should be on dashboard with domains
        if "dashboard" not in driver.current_url:
            driver.get(f"{APP_URL}/dashboard")
            time.sleep(2)
        
        # Wait for table to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "domainsTable"))
        )
        
        # Check if status is shown
        table_body = driver.find_element(By.CSS_SELECTOR, "#domainsTable tbody")
        
        # Look for status badges
        status_elements = driver.find_elements(By.CSS_SELECTOR, ".status")
        assert len(status_elements) > 0, "No status badges found"
        
        # Check if status shows UP or DOWN
        status_text = status_elements[0].text
        assert "UP" in status_text or "DOWN" in status_text, \
            f"Status doesn't show UP/DOWN: {status_text}"
        
        print(f"✓ Domain results display passed (Status: {status_text})")
        return True
        
    except Exception as e:
        print(f"✗ Domain results display failed: {e}")
        driver.save_screenshot("/tmp/results_failed.png")
        return False


def test_bulk_upload(driver):
    """Test 5: Bulk domain upload"""
    print("\n--- Test 5: Bulk Domain Upload ---")
    
    temp_file = None
    try:
        # Navigate to dashboard
        if "dashboard" not in driver.current_url:
            driver.get(f"{APP_URL}/dashboard")
            time.sleep(2)
        
        # Create temporary file
        temp_file = '/tmp/test_domains.txt'
        with open(temp_file, 'w') as f:
            f.write("example.com\n")
            f.write("github.com\n")
            f.write("stackoverflow.com\n")
        
        print(f"   Created: {temp_file}")
        
        # Upload file
        file_input = driver.find_element(By.ID, "fileInput")
        file_input.send_keys(temp_file)
        
        # Wait for upload to process
        time.sleep(2)
        
        # Handle alert popup
        try:
            alert = WebDriverWait(driver, 5).until(EC.alert_is_present())
            alert_text = alert.text
            print(f"   📢 Alert: {alert_text}")
            alert.accept()
        except:
            print("   No alert (ok)")
        
        # Wait for table to refresh
        time.sleep(3)
        
        # Verify domains added
        table_body = driver.find_element(By.CSS_SELECTOR, "#domainsTable tbody")
        rows = table_body.find_elements(By.TAG_NAME, "tr")
        
        print(f"   Found {len(rows)} domains in table")
        assert len(rows) >= 3, f"Expected at least 3 domains, found {len(rows)}"
        
        print("✓ Bulk upload passed")
        return True
        
    except Exception as e:
        print(f"✗ Bulk upload failed: {e}")
        driver.save_screenshot("/tmp/bulk_upload_failed.png")
        
        # Try to dismiss any lingering alert
        try:
            driver.switch_to.alert.accept()
        except:
            pass
        
        return False
    
    finally:
        # Cleanup temp file
        if temp_file and os.path.exists(temp_file):
            try:
                os.unlink(temp_file)
                print(f"   🧹 Cleaned up: {temp_file}")
            except:
                pass


def test_remove_domain(driver):
    """Test 6: Remove a domain"""
    print("\n--- Test 6: Remove Domain ---")
    
    try:
        # Navigate to dashboard
        if "dashboard" not in driver.current_url:
            driver.get(f"{APP_URL}/dashboard")
            time.sleep(2)
        
        # Get initial count
        table_body = driver.find_element(By.CSS_SELECTOR, "#domainsTable tbody")
        initial_rows = len(table_body.find_elements(By.TAG_NAME, "tr"))
        print(f"   Initial domains: {initial_rows}")
        
        if initial_rows == 0:
            print("   ⚠️  No domains to remove, skipping test")
            return True
        
        # Click first remove button
        remove_button = driver.find_element(By.CSS_SELECTOR, "button.remove-btn")
        domain_name = remove_button.get_attribute("data-domain")
        print(f"   Removing: {domain_name}")
        remove_button.click()
        
        # Handle confirmation dialog (Are you sure?)
        time.sleep(1)
        try:
            confirm_alert = driver.switch_to.alert
            print(f"   📢 Confirm: {confirm_alert.text}")
            confirm_alert.accept()
        except:
            print("   No confirmation dialog")
        
        # Handle success alert (Domain removed)
        time.sleep(2)
        try:
            success_alert = WebDriverWait(driver, 3).until(EC.alert_is_present())
            print(f"   📢 Success: {success_alert.text}")
            success_alert.accept()
        except:
            print("   No success alert")
        
        # Wait for table to refresh
        time.sleep(2)
        
        # Verify domain removed
        table_body = driver.find_element(By.CSS_SELECTOR, "#domainsTable tbody")
        new_rows = len(table_body.find_elements(By.TAG_NAME, "tr"))
        print(f"   Domains after removal: {new_rows}")
        
        assert new_rows < initial_rows, \
            f"Domain wasn't removed (had {initial_rows}, still have {new_rows})"
        
        print(f"✓ Remove domain passed ({initial_rows} → {new_rows})")
        return True
        
    except Exception as e:
        print(f"✗ Remove domain failed: {e}")
        driver.save_screenshot("/tmp/remove_failed.png")
        
        # Dismiss any lingering alerts
        try:
            driver.switch_to.alert.accept()
        except:
            pass
        
        return False


def run_all_ui_tests():
    """Run all UI tests"""
    print("=" * 70)
    print("🎨 DOMAIN MONITOR SYSTEM - UI TESTS")
    print("=" * 70)
    
    driver = setup_driver()
    
    try:
        # Wait for app to be ready
        if not wait_for_app(driver):
            print("\n❌ FAILED: Domain Monitor UI didn't load")
            driver.quit()
            sys.exit(1)
        
        # Run tests sequentially
        results = []
        
        results.append(test_register_flow(driver))
        results.append(test_login_flow(driver))
        results.append(test_add_single_domain(driver))
        results.append(test_domain_results(driver))
        results.append(test_bulk_upload(driver))
        results.append(test_remove_domain(driver))
        
        # Summary
        print("\n" + "=" * 70)
        passed = sum(results)
        total = len(results)
        print(f"📊 TEST RESULTS: {passed}/{total} PASSED")
        print("=" * 70)
        
        if all(results):
            print("\n🎉 ALL UI TESTS PASSED!")
            driver.quit()
            sys.exit(0)
        else:
            print("\n❌ SOME UI TESTS FAILED!")
            print("Check screenshots in /tmp/ for details")
            driver.quit()
            sys.exit(1)
            
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        driver.quit()
        sys.exit(1)


if __name__ == "__main__":
    run_all_ui_tests()

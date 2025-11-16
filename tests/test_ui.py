#!/usr/bin/env python3
"""
UI Tests for Domain Monitor System
Tests the web interface using Selenium
"""
import os
import sys
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

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
        driver.get(f"{APP_URL}/register")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "registerForm")))
        
        driver.find_element(By.ID, "username").send_keys(TEST_USER)
        driver.find_element(By.ID, "password").send_keys(TEST_PASSWORD)
        driver.find_element(By.CSS_SELECTOR, "button.form__button").click()
        
        # **FIXED**: Replaced sleep with an explicit wait for the URL to change.
        WebDriverWait(driver, 10).until(EC.url_contains("login"))
        
        current_url = driver.current_url
        assert "login" in current_url, f"Registration did not redirect to login. Current URL: {current_url}"
        
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
        driver.get(f"{APP_URL}/login")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "loginForm")))
        
        driver.find_element(By.ID, "username").send_keys(TEST_USER)
        driver.find_element(By.ID, "password").send_keys(TEST_PASSWORD)
        driver.find_element(By.CSS_SELECTOR, "button.form__button").click()
        
        WebDriverWait(driver, 10).until(EC.url_contains("dashboard"))
        
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
        if "dashboard" not in driver.current_url:
            driver.get(f"{APP_URL}/dashboard")
        
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "addDomainForm")))
        
        driver.find_element(By.CSS_SELECTOR, "#addDomainForm input[name='domain']").send_keys("google.com")
        driver.find_element(By.CSS_SELECTOR, "#addDomainForm button[type='submit']").click()
        
        # **FIXED**: Replaced sleep with a wait for the domain text to appear in the table.
        WebDriverWait(driver, 20).until(
            EC.text_to_be_present_in_element((By.CSS_SELECTOR, "#domainsTable tbody"), "google.com")
        )

        table_body = driver.find_element(By.CSS_SELECTOR, "#domainsTable tbody")
        assert "google.com" in table_body.text, "Added domain not found in table"
        
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
        if "dashboard" not in driver.current_url:
            driver.get(f"{APP_URL}/dashboard")
        
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "domainsTable")))
        
        status_elements = driver.find_elements(By.CSS_SELECTOR, ".status")
        assert len(status_elements) > 0, "No status badges found"
        
        status_text = status_elements[0].text
        assert "UP" in status_text or "DOWN" in status_text, f"Status doesn't show UP/DOWN: {status_text}"
        
        print(f"✓ Domain results display passed (Status: {status_text})")
        return True
        
    except Exception as e:
        print(f"✗ Domain results display failed: {e}")
        driver.save_screenshot("/tmp/results_failed.png")
        return False


def test_bulk_upload(driver):
    """Test 5: Bulk domain upload"""
    print("\n--- Test 5: Bulk Domain Upload ---")
    
    temp_file_path = None
    try:
        if "dashboard" not in driver.current_url:
            driver.get(f"{APP_URL}/dashboard")
        
        # Create temporary file
        temp_file_path = '/tmp/test_domains.txt'
        with open(temp_file_path, 'w') as f:
            f.write("github.com\n")
            f.write("stackoverflow.com\n")
        
        print(f"   Created: {temp_file_path}")
        
        driver.find_element(By.ID, "fileInput").send_keys(temp_file_path)
        
        try:
            alert = WebDriverWait(driver, 5).until(EC.alert_is_present())
            alert_text = alert.text
            print(f"   📢 Alert: {alert_text}")
            alert.accept()
        except:
            print("   No alert detected (which is normal).")
        
        # **FIXED**: Replaced sleep with a wait for new domains to appear in the table.
        WebDriverWait(driver, 20).until(
            EC.text_to_be_present_in_element((By.CSS_SELECTOR, "#domainsTable tbody"), "github.com")
        )

        table_body = driver.find_element(By.CSS_SELECTOR, "#domainsTable tbody")
        rows = table_body.find_elements(By.TAG_NAME, "tr")
        
        print(f"   Found {len(rows)} domains in table")
        assert len(rows) >= 2, f"Expected at least 2 domains, found {len(rows)}"
        
        print("✓ Bulk upload passed")
        return True
        
    except Exception as e:
        print(f"✗ Bulk upload failed: {e}")
        driver.save_screenshot("/tmp/bulk_upload_failed.png")
        return False
    
    finally:
        if temp_file_path and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)
            print(f"   🧹 Cleaned up: {temp_file_path}")


def test_remove_domain(driver):
    """Test 6: Remove a domain"""
    print("\n--- Test 6: Remove Domain ---")
    
    try:
        if "dashboard" not in driver.current_url:
            driver.get(f"{APP_URL}/dashboard")
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "domainsTable")))

        table_body = driver.find_element(By.CSS_SELECTOR, "#domainsTable tbody")
        initial_rows = len(table_body.find_elements(By.TAG_NAME, "tr"))
        print(f"   Initial domains: {initial_rows}")
        
        if initial_rows == 0:
            print("   ⚠️  No domains to remove, skipping test")
            return True
        
        remove_button = driver.find_element(By.CSS_SELECTOR, "button.remove-btn")
        domain_name = remove_button.get_attribute("data-domain")
        print(f"   Removing: {domain_name}")
        remove_button.click()
        
        # **FIXED**: Replaced sleep with an explicit wait for the confirmation dialog.
        confirm_alert = WebDriverWait(driver, 5).until(EC.alert_is_present())
        print(f"   📢 Confirm: {confirm_alert.text}")
        confirm_alert.accept()
        
        # **FIXED**: Replaced sleep with a wait for the number of rows to decrease.
        WebDriverWait(driver, 10).until(
            lambda d: len(d.find_elements(By.CSS_SELECTOR, "#domainsTable tbody tr")) < initial_rows
        )
        
        new_rows = len(driver.find_elements(By.CSS_SELECTOR, "#domainsTable tbody tr"))
        print(f"   Domains after removal: {new_rows}")
        
        assert new_rows < initial_rows, f"Domain wasn't removed (had {initial_rows}, still have {new_rows})"
        
        print(f"✓ Remove domain passed ({initial_rows} → {new_rows})")
        return True
        
    except Exception as e:
        print(f"✗ Remove domain failed: {e}")
        driver.save_screenshot("/tmp/remove_failed.png")
        return False


def run_all_ui_tests():
    """Run all UI tests"""
    print("=" * 70)
    print("🎨 DOMAIN MONITOR SYSTEM - UI TESTS")
    print("=" * 70)
    
    driver = setup_driver()
    
    try:
        if not wait_for_app(driver):
            print("\n❌ FAILED: Domain Monitor UI didn't load")
            driver.quit()
            sys.exit(1)
        
        results = []
        
        results.append(test_register_flow(driver))
        results.append(test_login_flow(driver))
        results.append(test_add_single_domain(driver))
        results.append(test_domain_results(driver))
        results.append(test_bulk_upload(driver))
        results.append(test_remove_domain(driver))
        
        print("\n" + "=" * 70)
        passed = sum(results)
        total = len(results)
        print(f"📊 TEST RESULTS: {passed}/{total} PASSED")
        print("=" * 70)
        
        if all(results):
            print("\n🎉 ALL UI TESTS PASSED!")
            sys.exit(0)
        else:
            print("\n❌ SOME UI TESTS FAILED!")
            print("Check screenshots in /tmp/ for details")
            sys.exit(1)
            
    finally:
        if driver:
            driver.quit()


if __name__ == "__main__":
    run_all_ui_tests()
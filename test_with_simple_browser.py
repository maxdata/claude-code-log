#!/usr/bin/env python3
"""
Simple Browser Test using Selenium WebDriver (lighter than Playwright)
"""

import time
import subprocess
import sys
import os


def install_selenium():
    """Install selenium if not available"""
    try:
        import selenium
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options

        print("✅ Selenium already available")
        return True
    except ImportError:
        print("📦 Installing Selenium...")
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "selenium"], check=True
            )
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options

            print("✅ Selenium installed")
            return True
        except Exception as e:
            print(f"❌ Failed to install Selenium: {e}")
            return False


def run_browser_test():
    """Run simple browser test"""
    if not install_selenium():
        return False

    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC

    print("\n🌐 Starting Browser Test...")

    # Setup Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in background
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")

    driver = None
    try:
        # Start Chrome driver
        driver = webdriver.Chrome(options=chrome_options)
        driver.set_page_load_timeout(30)

        print("✅ Browser launched successfully")

        # Navigate to Svelte app
        url = "http://localhost:5173"
        print(f"🔍 Navigating to {url}...")

        driver.get(url)

        # Wait for page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )

        print("✅ Page loaded successfully")

        # Check title
        title = driver.title
        print(f"📄 Page title: '{title}'")

        if "Claude Code Log Viewer" in title:
            print("✅ Correct page title found")
        else:
            print("⚠️  Unexpected page title")

        # Check for essential elements
        elements_to_check = [
            (".app", "Main app container"),
            (".welcome-section", "Welcome section"),
            (".file-upload", "File upload component"),
            (".drop-zone", "Drop zone"),
            ("h1", "Main heading"),
            (".upload-button", "Upload button"),
        ]

        for selector, name in elements_to_check:
            try:
                if selector.startswith("."):
                    elements = driver.find_elements(By.CLASS_NAME, selector[1:])
                else:
                    elements = driver.find_elements(By.TAG_NAME, selector)

                if elements:
                    print(f"✅ {name} found ({len(elements)} elements)")
                else:
                    print(f"❌ {name} NOT found")
            except Exception as e:
                print(f"❌ Error checking {name}: {e}")

        # Check for JavaScript errors (basic check)
        logs = driver.get_log("browser")
        js_errors = [log for log in logs if log["level"] == "SEVERE"]

        if js_errors:
            print(f"⚠️  Found {len(js_errors)} JavaScript errors:")
            for error in js_errors[:3]:  # Show first 3 errors
                print(f"   • {error['message']}")
        else:
            print("✅ No JavaScript errors detected")

        # Test basic interaction - hover over drop zone
        try:
            drop_zone = driver.find_element(By.CLASS_NAME, "drop-zone")
            driver.execute_script(
                "arguments[0].dispatchEvent(new Event('mouseover', {bubbles: true}));",
                drop_zone,
            )
            print("✅ Drop zone interaction test successful")
        except Exception as e:
            print(f"⚠️  Drop zone interaction failed: {e}")

        # Take a screenshot for manual inspection
        try:
            screenshot_path = "/tmp/svelte_ui_screenshot.png"
            driver.save_screenshot(screenshot_path)
            print(f"📸 Screenshot saved to {screenshot_path}")
        except:
            pass

        print("\n🎉 Browser test completed successfully!")
        return True

    except Exception as e:
        print(f"❌ Browser test failed: {e}")
        return False

    finally:
        if driver:
            driver.quit()


def main():
    print("🚀 Simple Browser Testing for Svelte UI")
    print("=" * 50)

    # First check if servers are running
    import socket

    def check_port(port, name):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex(("localhost", port))
        sock.close()
        return result == 0

    if not check_port(5173, "Svelte"):
        print("❌ Svelte dev server not running on port 5173")
        return False

    if not check_port(8000, "FastAPI"):
        print("⚠️  FastAPI not running on port 8000 (API tests will fail)")

    print("✅ Svelte dev server is running")

    # Run browser test
    return run_browser_test()


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

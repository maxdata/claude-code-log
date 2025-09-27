#!/usr/bin/env python3
"""
Simple UI Test Runner

This runs our comprehensive UI test with proper error handling
"""

import subprocess
import sys
import os


def install_playwright():
    """Install playwright if not available"""
    try:
        import playwright

        print("✅ Playwright already installed")
        return True
    except ImportError:
        print("📦 Installing Playwright...")
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "playwright==1.40.0"],
                check=True,
            )
            subprocess.run(
                [sys.executable, "-m", "playwright", "install", "chromium"], check=True
            )
            print("✅ Playwright installed successfully")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install Playwright: {e}")
            return False


def run_ui_tests():
    """Run the comprehensive UI tests"""
    # Change to the correct directory
    os.chdir("/Users/max/Documents/GitHub/claude-code-log/svelte-viewer")

    if not install_playwright():
        return False

    try:
        print("\n🧪 Running Comprehensive UI Tests...")
        print("=" * 50)

        # Run the test script
        result = subprocess.run(
            [sys.executable, "test_ui.py"], capture_output=False, text=True
        )

        return result.returncode == 0

    except Exception as e:
        print(f"❌ Failed to run UI tests: {e}")
        return False


if __name__ == "__main__":
    success = run_ui_tests()
    sys.exit(0 if success else 1)

#!/usr/bin/env python3
"""
Final UI Test - Complete Testing with Real Results

This script performs comprehensive testing of the Svelte UI and provides
a detailed report on functionality, issues, and recommendations.
"""

import json
import socket
import time
import urllib.request
import urllib.error
from typing import Dict, List, Tuple


class UITestResult:
    def __init__(self):
        self.tests_run = 0
        self.tests_passed = 0
        self.critical_issues = []
        self.warnings = []
        self.successes = []

    def add_success(self, test_name: str, details: str = ""):
        self.tests_run += 1
        self.tests_passed += 1
        self.successes.append((test_name, details))
        print(f"✅ {test_name}: {details}")

    def add_warning(self, test_name: str, issue: str):
        self.tests_run += 1
        self.warnings.append((test_name, issue))
        print(f"⚠️  {test_name}: {issue}")

    def add_critical(self, test_name: str, issue: str):
        self.tests_run += 1
        self.critical_issues.append((test_name, issue))
        print(f"❌ {test_name}: {issue}")

    def get_summary(self) -> Dict:
        return {
            "total_tests": self.tests_run,
            "passed": self.tests_passed,
            "critical_issues": len(self.critical_issues),
            "warnings": len(self.warnings),
            "success_rate": (self.tests_passed / self.tests_run * 100)
            if self.tests_run > 0
            else 0,
            "overall_status": "PASS" if len(self.critical_issues) == 0 else "FAIL",
        }


def test_port_connectivity(result: UITestResult):
    """Test if required ports are open"""
    print("\n🔍 Testing Port Connectivity")
    print("-" * 30)

    # Test FastAPI port 8000
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        connection_result = sock.connect_ex(("localhost", 8000))
        sock.close()

        if connection_result == 0:
            result.add_success("FastAPI Port 8000", "Open and accessible")
        else:
            result.add_critical("FastAPI Port 8000", "Closed - backend not running")
    except Exception as e:
        result.add_critical("FastAPI Port 8000", f"Connection error: {e}")

    # Test Svelte port 5173
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        connection_result = sock.connect_ex(("localhost", 5173))
        sock.close()

        if connection_result == 0:
            result.add_success("Svelte Port 5173", "Open and accessible")
        else:
            result.add_critical("Svelte Port 5173", "Closed - frontend not running")
    except Exception as e:
        result.add_critical("Svelte Port 5173", f"Connection error: {e}")


def test_http_endpoints(result: UITestResult):
    """Test HTTP endpoint accessibility"""
    print("\n🌐 Testing HTTP Endpoints")
    print("-" * 30)

    # Test FastAPI health endpoint
    try:
        req = urllib.request.Request("http://localhost:8000/health")
        with urllib.request.urlopen(req, timeout=10) as response:
            status = response.status
            content = response.read().decode()

            if status == 200:
                result.add_success(
                    "FastAPI Health Endpoint", f"HTTP {status} - {content[:50]}"
                )
            else:
                result.add_warning(
                    "FastAPI Health Endpoint", f"Unexpected status: HTTP {status}"
                )

    except urllib.error.URLError as e:
        result.add_critical("FastAPI Health Endpoint", f"Connection failed: {e}")
    except Exception as e:
        result.add_critical("FastAPI Health Endpoint", f"Request error: {e}")

    # Test FastAPI projects endpoint
    try:
        req = urllib.request.Request("http://localhost:8000/api/projects")
        with urllib.request.urlopen(req, timeout=10) as response:
            status = response.status

            if status == 200:
                result.add_success(
                    "FastAPI Projects API", f"HTTP {status} - API accessible"
                )
            else:
                result.add_warning(
                    "FastAPI Projects API", f"Unexpected status: HTTP {status}"
                )

    except urllib.error.URLError as e:
        result.add_warning("FastAPI Projects API", f"Connection failed: {e}")
    except Exception as e:
        result.add_warning("FastAPI Projects API", f"Request error: {e}")

    # Test Svelte frontend
    try:
        req = urllib.request.Request("http://localhost:5173")
        with urllib.request.urlopen(req, timeout=10) as response:
            status = response.status
            content = response.read(4000).decode("utf-8", errors="ignore")

            if status == 200:
                result.add_success(
                    "Svelte Frontend", f"HTTP {status} - Page loads successfully"
                )
                return content
            else:
                result.add_critical("Svelte Frontend", f"Failed to load: HTTP {status}")
                return None

    except urllib.error.URLError as e:
        result.add_critical("Svelte Frontend", f"Connection failed: {e}")
        return None
    except Exception as e:
        result.add_critical("Svelte Frontend", f"Request error: {e}")
        return None


def test_ui_content(content: str, result: UITestResult):
    """Test UI content and structure"""
    if not content:
        result.add_critical("UI Content Analysis", "No content to analyze")
        return

    print("\n🎨 Testing UI Content")
    print("-" * 30)

    # Check page title
    if "Claude Code Log Viewer" in content:
        result.add_success("Page Title", "Correct title found")
    else:
        result.add_warning(
            "Page Title", "Expected title 'Claude Code Log Viewer' not found"
        )

    # Check for essential CSS classes/components
    ui_components = [
        ("Main App Container", ['class="app"', "class='app'", "class=app"]),
        ("Welcome Section", ["welcome-section"]),
        ("File Upload Component", ["file-upload"]),
        ("Drop Zone", ["drop-zone"]),
        ("Upload Button", ["upload-button"]),
    ]

    for component_name, selectors in ui_components:
        found = any(selector in content for selector in selectors)
        if found:
            result.add_success(f"UI Component: {component_name}", "Found in DOM")
        else:
            severity = (
                "critical"
                if component_name in ["Main App Container", "File Upload Component"]
                else "warning"
            )
            if severity == "critical":
                result.add_critical(
                    f"UI Component: {component_name}", "Missing from DOM"
                )
            else:
                result.add_warning(
                    f"UI Component: {component_name}", "Missing from DOM"
                )

    # Check for Svelte/SvelteKit indicators
    svelte_indicators = ["svelte", "sveltekit", "__vite__", "_app"]
    found_indicators = sum(
        1 for indicator in svelte_indicators if indicator in content.lower()
    )

    if found_indicators >= 2:
        result.add_success(
            "Svelte Framework", f"Detected ({found_indicators} indicators)"
        )
    else:
        result.add_warning(
            "Svelte Framework", "Framework indicators not clearly detected"
        )

    # Check for potential JavaScript/CSS loading
    if "<script" in content and ("src=" in content or "type=" in content):
        result.add_success("JavaScript Loading", "Script tags detected")
    else:
        result.add_warning("JavaScript Loading", "No script tags found")

    if "<link" in content and "stylesheet" in content:
        result.add_success("CSS Loading", "Stylesheet links detected")
    else:
        result.add_warning("CSS Loading", "No stylesheet links found")


def test_cors_configuration(result: UITestResult):
    """Test CORS configuration between frontend and backend"""
    print("\n🔗 Testing CORS Configuration")
    print("-" * 30)

    try:
        # Create a request with CORS headers
        req = urllib.request.Request("http://localhost:8000/api/projects")
        req.add_header("Origin", "http://localhost:5173")
        req.add_header("Access-Control-Request-Method", "GET")

        with urllib.request.urlopen(req, timeout=5) as response:
            cors_headers = [
                header
                for header in response.headers.keys()
                if header.lower().startswith("access-control")
            ]

            if cors_headers:
                result.add_success(
                    "CORS Headers", f"Found {len(cors_headers)} CORS headers"
                )
            else:
                result.add_warning("CORS Headers", "No CORS headers detected")

    except Exception as e:
        result.add_warning("CORS Configuration", f"Could not test CORS: {e}")


def generate_final_report(result: UITestResult):
    """Generate comprehensive final report"""
    summary = result.get_summary()

    print("\n" + "=" * 60)
    print("📊 COMPREHENSIVE UI TEST REPORT")
    print("=" * 60)

    # Overall status
    status_emoji = "✅" if summary["overall_status"] == "PASS" else "❌"
    print(f"\n{status_emoji} Overall Status: {summary['overall_status']}")
    print(f"📈 Tests Run: {summary['total_tests']}")
    print(f"✅ Tests Passed: {summary['passed']}")
    print(f"❌ Critical Issues: {summary['critical_issues']}")
    print(f"⚠️  Warnings: {summary['warnings']}")
    print(f"📊 Success Rate: {summary['success_rate']:.1f}%")

    # Critical issues section
    if result.critical_issues:
        print(f"\n🚨 CRITICAL ISSUES (Must Fix):")
        for test_name, issue in result.critical_issues:
            print(f"   • {test_name}: {issue}")

    # Warnings section
    if result.warnings:
        print(f"\n⚠️  WARNINGS (Should Address):")
        for test_name, issue in result.warnings:
            print(f"   • {test_name}: {issue}")

    # Successes section
    if result.successes:
        print(f"\n✅ WORKING CORRECTLY:")
        for test_name, details in result.successes:
            print(f"   • {test_name}: {details}")

    print(f"\n{'=' * 60}")

    # Recommendations
    print("💡 RECOMMENDATIONS:")

    if summary["overall_status"] == "PASS":
        print("   🎉 UI is working correctly! Ready for use.")
        print("\n   📋 Manual testing checklist:")
        print("   1. Open http://localhost:5173 in browser")
        print("   2. Verify file upload interface is visible")
        print("   3. Test drag-and-drop with .jsonl files")
        print("   4. Check browser console for errors")
        print("   5. Test filtering and UI interactions")
        print("   6. Verify API communication works")
    else:
        print("   🔧 Fix the following issues:")

        if any("Port" in issue[0] for issue in result.critical_issues):
            print("   • Start required servers:")
            if any("5173" in issue[1] for issue in result.critical_issues):
                print("     - Svelte: cd svelte-viewer && npm run dev")
            if any("8000" in issue[1] for issue in result.critical_issues):
                print("     - FastAPI: uvicorn server:app --reload --port 8000")

        if any("UI Component" in issue[0] for issue in result.critical_issues):
            print("   • Check Svelte build configuration")
            print("   • Verify component imports and exports")

        print("\n   🔍 After fixing issues, rerun this test")

    return summary["overall_status"] == "PASS"


def main():
    """Main test execution function"""
    print("🚀 Comprehensive Svelte UI Testing Suite")
    print("Claude Code Log Viewer - UI Functionality Test")
    print("=" * 60)

    result = UITestResult()

    # Run all test suites
    test_port_connectivity(result)
    content = test_http_endpoints(result)
    test_ui_content(content, result)
    test_cors_configuration(result)

    # Generate final report
    success = generate_final_report(result)

    return success


if __name__ == "__main__":
    try:
        success = main()
        exit_code = 0 if success else 1
        print(f"\nTest completed with exit code: {exit_code}")
    except KeyboardInterrupt:
        print("\n⏹️  Testing interrupted by user")
        exit_code = 1
    except Exception as e:
        print(f"\n💥 Testing failed with error: {e}")
        exit_code = 1

# Execute the test immediately
main()

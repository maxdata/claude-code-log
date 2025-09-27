#!/usr/bin/env python3
"""
Comprehensive UI Test Runner for Claude Code Log Svelte Interface
Tests both FastAPI server (port 8000) and Svelte dev server (port 5173)
"""

import json
import socket
import time
import urllib.request
import urllib.error
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Dict, List, Any

# Configuration
FASTAPI_URL = "http://localhost:8000"
SVELTE_URL = "http://localhost:5173"
TEST_TIMEOUT = 10


class UITestResults:
    def __init__(self):
        self.results = {
            "server_connectivity": [],
            "endpoint_tests": [],
            "ui_component_tests": [],
            "content_analysis": [],
            "issues": [],
            "summary": {},
        }

    def add_test(self, category: str, test_name: str, status: str, details: str = ""):
        """Add a test result"""
        result = {
            "test_name": test_name,
            "status": status,  # PASS, FAIL, WARNING
            "details": details,
            "timestamp": time.time(),
        }
        self.results[category].append(result)

        # Print real-time feedback
        emoji = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{emoji} {test_name}: {details}")

        if status == "FAIL":
            self.results["issues"].append(f"CRITICAL: {test_name} - {details}")
        elif status == "WARNING":
            self.results["issues"].append(f"WARNING: {test_name} - {details}")


def test_port_connectivity(results: UITestResults):
    """Test if both servers are running"""
    print("\n🔍 Testing Server Connectivity")
    print("-" * 40)

    # Test FastAPI port 8000
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        result = sock.connect_ex(("localhost", 8000))
        sock.close()

        if result == 0:
            results.add_test(
                "server_connectivity", "FastAPI Port 8000", "PASS", "Server responding"
            )
        else:
            results.add_test(
                "server_connectivity",
                "FastAPI Port 8000",
                "FAIL",
                "Port closed - server not running",
            )
    except Exception as e:
        results.add_test(
            "server_connectivity", "FastAPI Port 8000", "FAIL", f"Connection error: {e}"
        )

    # Test Svelte port 5173
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        result = sock.connect_ex(("localhost", 5173))
        sock.close()

        if result == 0:
            results.add_test(
                "server_connectivity", "Svelte Port 5173", "PASS", "Server responding"
            )
        else:
            results.add_test(
                "server_connectivity",
                "Svelte Port 5173",
                "FAIL",
                "Port closed - server not running",
            )
    except Exception as e:
        results.add_test(
            "server_connectivity", "Svelte Port 5173", "FAIL", f"Connection error: {e}"
        )


def test_fastapi_endpoints(results: UITestResults):
    """Test FastAPI backend endpoints"""
    print("\n🔍 Testing FastAPI Endpoints")
    print("-" * 40)

    endpoints = [
        ("/health", "Health Check"),
        ("/api/projects", "Projects API"),
        ("/", "Main Route (serving Svelte app)"),
    ]

    for endpoint, name in endpoints:
        try:
            url = f"{FASTAPI_URL}{endpoint}"
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=TEST_TIMEOUT) as response:
                status = response.status
                content = response.read(1000).decode("utf-8", errors="ignore")

                if status == 200:
                    results.add_test("endpoint_tests", name, "PASS", f"HTTP {status}")

                    # Special checks for different endpoints
                    if endpoint == "/health":
                        if "healthy" in content.lower():
                            results.add_test(
                                "endpoint_tests",
                                "Health Response Content",
                                "PASS",
                                "Contains 'healthy' status",
                            )
                        else:
                            results.add_test(
                                "endpoint_tests",
                                "Health Response Content",
                                "WARNING",
                                "Unexpected health response",
                            )

                    elif endpoint == "/":
                        if "<!DOCTYPE html>" in content:
                            results.add_test(
                                "endpoint_tests",
                                "Main Route HTML",
                                "PASS",
                                "Returns valid HTML",
                            )
                        else:
                            results.add_test(
                                "endpoint_tests",
                                "Main Route HTML",
                                "WARNING",
                                "Doesn't return HTML content",
                            )
                else:
                    results.add_test(
                        "endpoint_tests", name, "WARNING", f"HTTP {status}"
                    )

        except urllib.error.URLError as e:
            results.add_test("endpoint_tests", name, "FAIL", f"Connection failed: {e}")
        except Exception as e:
            results.add_test("endpoint_tests", name, "FAIL", f"Request error: {e}")


def test_svelte_frontend(results: UITestResults):
    """Test Svelte frontend content and structure"""
    print("\n🔍 Testing Svelte Frontend")
    print("-" * 40)

    try:
        req = urllib.request.Request(SVELTE_URL)
        with urllib.request.urlopen(req, timeout=TEST_TIMEOUT) as response:
            status = response.status
            content = response.read(5000).decode("utf-8", errors="ignore")

            if status == 200:
                results.add_test(
                    "ui_component_tests", "Svelte App Load", "PASS", f"HTTP {status}"
                )
                return analyze_ui_content(content, results)
            else:
                results.add_test(
                    "ui_component_tests", "Svelte App Load", "FAIL", f"HTTP {status}"
                )
                return None

    except urllib.error.URLError as e:
        results.add_test(
            "ui_component_tests", "Svelte App Load", "FAIL", f"Connection failed: {e}"
        )
        return None
    except Exception as e:
        results.add_test(
            "ui_component_tests", "Svelte App Load", "FAIL", f"Request error: {e}"
        )
        return None


def analyze_ui_content(content: str, results: UITestResults):
    """Analyze UI content for expected components"""
    print("\n🎨 Analyzing UI Content")
    print("-" * 40)

    # Check page title
    if "Claude Code Log Viewer" in content:
        results.add_test(
            "content_analysis", "Page Title", "PASS", "Correct title found"
        )
    else:
        results.add_test(
            "content_analysis", "Page Title", "WARNING", "Expected title not found"
        )

    # Check for essential UI components
    ui_components = [
        ('class="app"', "Main App Container"),
        ('class="welcome-section"', "Welcome Section"),
        ('class="file-upload"', "File Upload Component"),
        ('class="drop-zone"', "Drop Zone"),
        ("upload-button", "Upload Button"),
        ("drag", "Drag Functionality"),
        ("drop", "Drop Functionality"),
    ]

    for selector, component_name in ui_components:
        if selector in content:
            results.add_test("content_analysis", component_name, "PASS", "Found in DOM")
        else:
            severity = (
                "FAIL"
                if component_name in ["Main App Container", "File Upload Component"]
                else "WARNING"
            )
            results.add_test(
                "content_analysis", component_name, severity, "Missing from DOM"
            )

    # Check for JavaScript/CSS loading
    if "<script" in content and ("src=" in content or "type=" in content):
        results.add_test(
            "content_analysis", "JavaScript Loading", "PASS", "Script tags detected"
        )
    else:
        results.add_test(
            "content_analysis", "JavaScript Loading", "WARNING", "No script tags found"
        )

    if "<link" in content and "stylesheet" in content:
        results.add_test(
            "content_analysis", "CSS Loading", "PASS", "Stylesheet links detected"
        )
    else:
        results.add_test(
            "content_analysis", "CSS Loading", "WARNING", "No stylesheet links found"
        )

    # Check for Svelte/Vite indicators
    svelte_indicators = ["svelte", "vite", "_app", "__vite__"]
    found_indicators = sum(
        1 for indicator in svelte_indicators if indicator in content.lower()
    )

    if found_indicators >= 2:
        results.add_test(
            "content_analysis",
            "Svelte Framework",
            "PASS",
            f"Detected ({found_indicators} indicators)",
        )
    else:
        results.add_test(
            "content_analysis",
            "Svelte Framework",
            "WARNING",
            "Framework indicators not clearly detected",
        )

    return content


def test_cors_configuration(results: UITestResults):
    """Test CORS configuration between frontend and backend"""
    print("\n🔗 Testing CORS Configuration")
    print("-" * 40)

    try:
        req = urllib.request.Request(f"{FASTAPI_URL}/api/projects")
        req.add_header("Origin", SVELTE_URL)

        with urllib.request.urlopen(req, timeout=5) as response:
            cors_headers = [
                header
                for header in response.headers.keys()
                if header.lower().startswith("access-control")
            ]

            if cors_headers:
                results.add_test(
                    "endpoint_tests",
                    "CORS Headers",
                    "PASS",
                    f"Found {len(cors_headers)} CORS headers",
                )
            else:
                results.add_test(
                    "endpoint_tests",
                    "CORS Headers",
                    "WARNING",
                    "No CORS headers detected",
                )

    except Exception as e:
        results.add_test(
            "endpoint_tests",
            "CORS Configuration",
            "WARNING",
            f"Could not test CORS: {e}",
        )


def generate_comprehensive_report(results: UITestResults):
    """Generate final comprehensive report"""
    print("\n" + "=" * 60)
    print("📊 COMPREHENSIVE UI TEST REPORT")
    print("=" * 60)

    # Count results
    total_tests = sum(
        len(category)
        for category in results.results.values()
        if isinstance(category, list)
    )
    passed_tests = sum(
        len([test for test in category if test.get("status") == "PASS"])
        for category in results.results.values()
        if isinstance(category, list)
    )
    failed_tests = sum(
        len([test for test in category if test.get("status") == "FAIL"])
        for category in results.results.values()
        if isinstance(category, list)
    )
    warnings = sum(
        len([test for test in category if test.get("status") == "WARNING"])
        for category in results.results.values()
        if isinstance(category, list)
    )

    critical_issues = len(
        [issue for issue in results.results["issues"] if issue.startswith("CRITICAL")]
    )

    # Overall status
    if critical_issues == 0:
        overall_status = "PASS" if warnings == 0 else "PARTIAL"
        status_emoji = "✅" if warnings == 0 else "⚠️"
    else:
        overall_status = "FAIL"
        status_emoji = "❌"

    print(f"\n{status_emoji} Overall Status: {overall_status}")
    print(f"📈 Total Tests: {total_tests}")
    print(f"✅ Passed: {passed_tests}")
    print(f"❌ Failed: {failed_tests}")
    print(f"⚠️  Warnings: {warnings}")
    print(f"🚨 Critical Issues: {critical_issues}")

    if results.results["issues"]:
        print(f"\n🚨 ISSUES FOUND:")
        for issue in results.results["issues"]:
            print(f"   • {issue}")

    # Detailed category results
    for category, tests in results.results.items():
        if isinstance(tests, list) and tests:
            print(f"\n📋 {category.replace('_', ' ').title()}:")
            for test in tests:
                emoji = (
                    "✅"
                    if test["status"] == "PASS"
                    else "❌"
                    if test["status"] == "FAIL"
                    else "⚠️"
                )
                print(f"   {emoji} {test['test_name']}: {test['details']}")

    print(f"\n{'=' * 60}")

    # Recommendations
    print("💡 RECOMMENDATIONS:")

    if overall_status == "PASS":
        print("   🎉 UI is working perfectly! All critical tests passed.")
        print("\n   📋 Manual testing checklist:")
        print("   1. Open http://localhost:8000 in browser (FastAPI serving Svelte)")
        print("   2. OR open http://localhost:5173 (Svelte dev server)")
        print("   3. Verify file upload interface is visible and interactive")
        print("   4. Test drag-and-drop functionality with .jsonl files")
        print("   5. Check browser console for JavaScript errors")
        print("   6. Test API communication by monitoring Network tab")
        print("   7. Verify hover effects on upload zone")
        print("   8. Test responsive design by resizing browser window")

    elif overall_status == "PARTIAL":
        print("   ⚠️  Some minor issues detected, but core functionality should work")
        print("   🔍 Review warnings above and test manually")

    else:
        print("   🚨 Critical issues must be fixed before UI will work properly:")

        if any("Port" in issue for issue in results.results["issues"]):
            print("   • Start required servers:")
            if any("8000" in issue for issue in results.results["issues"]):
                print(
                    "     - FastAPI: cd /path/to/project && uv run uvicorn claude_code_log.server:app --host 127.0.0.1 --port 8000 --reload"
                )
            if any("5173" in issue for issue in results.results["issues"]):
                print("     - Svelte: cd svelte-viewer && npm run dev")

        if any("DOM" in issue for issue in results.results["issues"]):
            print("   • Check Svelte build and component structure")
            print("   • Verify all imports and component exports")

        print("   🔄 Rerun this test after fixing issues")

    print("\n📍 Key URLs:")
    print(f"   • FastAPI Backend: {FASTAPI_URL}")
    print(f"   • FastAPI Health: {FASTAPI_URL}/health")
    print(f"   • FastAPI serving Svelte: {FASTAPI_URL}/")
    print(f"   • Svelte Dev Server: {SVELTE_URL}")
    print(f"   • Projects API: {FASTAPI_URL}/api/projects")

    # Store summary
    results.results["summary"] = {
        "overall_status": overall_status,
        "total_tests": total_tests,
        "passed": passed_tests,
        "failed": failed_tests,
        "warnings": warnings,
        "critical_issues": critical_issues,
    }

    return overall_status == "PASS"


def main():
    """Main test execution"""
    print("🚀 Comprehensive Claude Code Log UI Testing")
    print(
        "Testing Svelte UI at http://localhost:8000 (FastAPI) and http://localhost:5173"
    )
    print("=" * 60)

    results = UITestResults()

    # Run test suites
    test_port_connectivity(results)
    test_fastapi_endpoints(results)
    test_svelte_frontend(results)
    test_cors_configuration(results)

    # Generate comprehensive report
    success = generate_comprehensive_report(results)

    return success


if __name__ == "__main__":
    try:
        success = main()
        exit_code = 0 if success else 1
        print(f"\n🏁 Test completed with exit code: {exit_code}")
        sys.exit(exit_code)

    except KeyboardInterrupt:
        print("\n⏹️  Testing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Testing failed with error: {e}")
        sys.exit(1)

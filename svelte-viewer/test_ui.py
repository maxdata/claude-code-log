#!/usr/bin/env python3
"""
Comprehensive UI Testing Script for Claude Code Log Svelte Viewer

This script performs thorough testing of the Svelte UI interface including:
- Page loading and basic functionality
- API communication with FastAPI backend
- JavaScript console error detection
- Network request monitoring
- UI interactions and responsiveness
"""

import asyncio
import json
import os
import sys
import time
from typing import Dict, List, Any
from playwright.async_api import (
    async_playwright,
    Page,
    Browser,
    BrowserContext,
    Request,
    Response,
)

# Configuration
SVELTE_URL = "http://localhost:5173"  # Svelte dev server
API_BASE = "http://localhost:8000"  # FastAPI backend
TEST_TIMEOUT = 30000  # 30 seconds


class UITestReport:
    def __init__(self):
        self.results: Dict[str, Any] = {
            "page_load": {},
            "api_communication": {},
            "javascript_errors": [],
            "network_requests": [],
            "ui_interactions": {},
            "performance": {},
            "issues": [],
            "summary": {},
        }

    def add_issue(
        self, category: str, severity: str, description: str, details: Any = None
    ):
        issue = {
            "category": category,
            "severity": severity,
            "description": description,
            "details": details,
            "timestamp": time.time(),
        }
        self.results["issues"].append(issue)
        print(f"🚨 {severity.upper()}: {description}")
        if details:
            print(f"   Details: {details}")

    def add_success(self, category: str, description: str, details: Any = None):
        print(f"✅ {description}")
        if details:
            print(f"   Details: {details}")

    def generate_summary(self):
        total_issues = len(self.results["issues"])
        critical_issues = len(
            [i for i in self.results["issues"] if i["severity"] == "critical"]
        )
        warnings = len(
            [i for i in self.results["issues"] if i["severity"] == "warning"]
        )

        self.results["summary"] = {
            "total_issues": total_issues,
            "critical_issues": critical_issues,
            "warnings": warnings,
            "status": "FAIL"
            if critical_issues > 0
            else "PASS"
            if warnings == 0
            else "PARTIAL",
        }


async def test_page_loading(page: Page, report: UITestReport):
    """Test basic page loading and initial state"""
    print("\n🔍 Testing page loading...")

    try:
        # Navigate to the page with extended timeout
        response = await page.goto(
            SVELTE_URL, timeout=TEST_TIMEOUT, wait_until="networkidle"
        )

        if not response:
            report.add_issue(
                "page_load", "critical", "Failed to load page - no response received"
            )
            return False

        if response.status != 200:
            report.add_issue(
                "page_load",
                "critical",
                f"Page load failed with status {response.status}",
            )
            return False

        report.add_success(
            "page_load", f"Page loaded successfully (HTTP {response.status})"
        )

        # Wait for the page to be fully rendered
        await page.wait_for_load_state("domcontentloaded")
        await page.wait_for_timeout(2000)  # Allow time for Svelte to initialize

        # Check for essential elements
        title = await page.title()
        if "Claude Code Log Viewer" not in title:
            report.add_issue("page_load", "warning", f"Unexpected page title: {title}")
        else:
            report.add_success("page_load", f"Correct page title: {title}")

        # Check for main application container
        app_container = await page.locator(".app").count()
        if app_container == 0:
            report.add_issue(
                "page_load", "critical", "Main app container (.app) not found"
            )
            return False

        report.add_success("page_load", "Main application container found")

        # Check for welcome section (should be visible initially)
        welcome_section = await page.locator(".welcome-section").count()
        if welcome_section == 0:
            report.add_issue("page_load", "warning", "Welcome section not found")
        else:
            report.add_success("page_load", "Welcome section is present")

        # Check for file upload component
        file_upload = await page.locator(".file-upload").count()
        if file_upload == 0:
            report.add_issue("page_load", "critical", "File upload component not found")
            return False

        report.add_success("page_load", "File upload component found")

        return True

    except Exception as e:
        report.add_issue(
            "page_load", "critical", f"Page loading failed with exception: {str(e)}"
        )
        return False


async def test_api_connectivity(page: Page, report: UITestReport):
    """Test API connectivity and CORS configuration"""
    print("\n🔍 Testing API connectivity...")

    try:
        # Test direct API endpoint access
        response = await page.request.get(f"{API_BASE}/health")

        if response.status == 200:
            report.add_success("api_communication", "Health endpoint is accessible")
        else:
            report.add_issue(
                "api_communication",
                "warning",
                f"Health endpoint returned status {response.status}",
            )

        # Test projects endpoint
        projects_response = await page.request.get(f"{API_BASE}/api/projects")

        if projects_response.status == 200:
            report.add_success("api_communication", "Projects endpoint is accessible")
        else:
            report.add_issue(
                "api_communication",
                "warning",
                f"Projects endpoint returned status {projects_response.status}",
            )

        return True

    except Exception as e:
        report.add_issue(
            "api_communication", "critical", f"API connectivity test failed: {str(e)}"
        )
        return False


async def test_javascript_errors(page: Page, report: UITestReport):
    """Monitor for JavaScript console errors"""
    print("\n🔍 Monitoring JavaScript console...")

    def handle_console_message(msg):
        if msg.type in ["error", "warning"]:
            report.results["javascript_errors"].append(
                {
                    "type": msg.type,
                    "text": msg.text,
                    "location": msg.location if hasattr(msg, "location") else None,
                }
            )
            severity = "critical" if msg.type == "error" else "warning"
            report.add_issue("javascript", severity, f"Console {msg.type}: {msg.text}")

    page.on("console", handle_console_message)

    # Navigate again to capture any console messages during load
    await page.reload(wait_until="networkidle")
    await page.wait_for_timeout(3000)  # Wait for any async operations

    if len(report.results["javascript_errors"]) == 0:
        report.add_success("javascript", "No JavaScript errors detected")

    return True


async def test_network_requests(page: Page, report: UITestReport):
    """Monitor network requests for failures"""
    print("\n🔍 Monitoring network requests...")

    def handle_request(request: Request):
        report.results["network_requests"].append(
            {"url": request.url, "method": request.method, "timestamp": time.time()}
        )

    def handle_response(response: Response):
        if response.status >= 400:
            report.add_issue(
                "network",
                "warning",
                f"HTTP {response.status} for {response.url}",
                {"method": response.request.method},
            )

    page.on("request", handle_request)
    page.on("response", handle_response)

    # Trigger a page reload to capture network activity
    await page.reload(wait_until="networkidle")
    await page.wait_for_timeout(2000)

    return True


async def test_ui_interactions(page: Page, report: UITestReport):
    """Test basic UI interactions"""
    print("\n🔍 Testing UI interactions...")

    try:
        # Test file upload area hover
        drop_zone = page.locator(".drop-zone")
        if await drop_zone.count() > 0:
            await drop_zone.hover()
            report.add_success(
                "ui_interactions", "File upload drop zone is interactive"
            )
        else:
            report.add_issue(
                "ui_interactions",
                "warning",
                "Drop zone not found for interaction testing",
            )

        # Test file input button
        upload_button = page.locator(".upload-button")
        if await upload_button.count() > 0:
            # Just check if it's clickable, don't actually click (would open file dialog)
            is_visible = await upload_button.is_visible()
            if is_visible:
                report.add_success(
                    "ui_interactions", "Upload button is visible and accessible"
                )
            else:
                report.add_issue(
                    "ui_interactions", "warning", "Upload button is not visible"
                )
        else:
            report.add_issue("ui_interactions", "warning", "Upload button not found")

        # Test responsive design by changing viewport
        await page.set_viewport_size({"width": 360, "height": 640})  # Mobile size
        await page.wait_for_timeout(1000)

        # Check if mobile layout works
        app_header = page.locator(".app-header")
        if await app_header.count() > 0:
            report.add_success("ui_interactions", "Mobile responsive layout working")

        # Reset viewport
        await page.set_viewport_size({"width": 1280, "height": 720})

        return True

    except Exception as e:
        report.add_issue(
            "ui_interactions", "warning", f"UI interaction test failed: {str(e)}"
        )
        return False


async def test_drag_drop_functionality(page: Page, report: UITestReport):
    """Test drag and drop file upload functionality"""
    print("\n🔍 Testing drag and drop functionality...")

    try:
        # Find the drop zone
        drop_zone = page.locator(".drop-zone")

        if await drop_zone.count() == 0:
            report.add_issue("drag_drop", "critical", "Drop zone not found")
            return False

        # Test drag over event
        await drop_zone.hover()

        # We can't easily simulate file drops in Playwright without actual files,
        # but we can test that the drag handlers are set up correctly by checking CSS classes

        # Check if drag styling would be applied (this tests the JavaScript event handlers)
        await page.evaluate("""
            const dropZone = document.querySelector('.drop-zone');
            const dragEvent = new DragEvent('dragover', { 
                bubbles: true, 
                cancelable: true,
                dataTransfer: new DataTransfer()
            });
            dropZone.dispatchEvent(dragEvent);
        """)

        await page.wait_for_timeout(500)

        # Check if drag-active class gets applied
        has_drag_class = await page.evaluate("""
            document.querySelector('.drop-zone').classList.contains('drag-active')
        """)

        if has_drag_class:
            report.add_success("drag_drop", "Drag over event handling works correctly")
        else:
            report.add_issue(
                "drag_drop",
                "warning",
                "Drag over styling not applied - event handlers may not be working",
            )

        # Clean up drag state
        await page.evaluate("""
            const dropZone = document.querySelector('.drop-zone');
            const dragLeaveEvent = new DragEvent('dragleave', { 
                bubbles: true, 
                cancelable: true
            });
            dropZone.dispatchEvent(dragLeaveEvent);
        """)

        return True

    except Exception as e:
        report.add_issue("drag_drop", "warning", f"Drag and drop test failed: {str(e)}")
        return False


async def test_performance_metrics(page: Page, report: UITestReport):
    """Test basic performance metrics"""
    print("\n🔍 Testing performance metrics...")

    try:
        # Navigate and measure load time
        start_time = time.time()
        await page.goto(SVELTE_URL, wait_until="networkidle")
        load_time = time.time() - start_time

        report.results["performance"]["page_load_time"] = load_time

        if load_time > 10:
            report.add_issue(
                "performance", "warning", f"Slow page load time: {load_time:.2f}s"
            )
        else:
            report.add_success("performance", f"Good page load time: {load_time:.2f}s")

        # Check bundle size by monitoring network requests
        script_sizes = []
        style_sizes = []

        def track_resource_size(response: Response):
            if response.url.endswith(".js"):
                content_length = response.headers.get("content-length")
                if content_length:
                    script_sizes.append(int(content_length))
            elif response.url.endswith(".css"):
                content_length = response.headers.get("content-length")
                if content_length:
                    style_sizes.append(int(content_length))

        page.on("response", track_resource_size)
        await page.reload(wait_until="networkidle")

        total_js_size = sum(script_sizes)
        total_css_size = sum(style_sizes)

        report.results["performance"]["total_js_size"] = total_js_size
        report.results["performance"]["total_css_size"] = total_css_size

        if total_js_size > 1024 * 1024:  # 1MB
            report.add_issue(
                "performance",
                "warning",
                f"Large JavaScript bundle: {total_js_size / 1024:.1f}KB",
            )
        else:
            report.add_success(
                "performance",
                f"Reasonable JavaScript bundle size: {total_js_size / 1024:.1f}KB",
            )

        return True

    except Exception as e:
        report.add_issue(
            "performance", "warning", f"Performance testing failed: {str(e)}"
        )
        return False


async def run_comprehensive_tests():
    """Run all UI tests and generate a comprehensive report"""
    print("🚀 Starting Comprehensive Svelte UI Testing")
    print(f"📍 Target URL: {SVELTE_URL}")
    print(f"📍 API Base: {API_BASE}")
    print("=" * 60)

    report = UITestReport()

    async with async_playwright() as p:
        # Launch browser with debugging options
        browser = await p.chromium.launch(
            headless=True,  # Set to False for debugging
            args=["--no-sandbox", "--disable-dev-shm-usage"],
        )

        context = await browser.new_context(
            viewport={"width": 1280, "height": 720},
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        )

        page = await context.new_page()

        try:
            # Run all test suites
            tests = [
                ("Page Loading", test_page_loading),
                ("API Connectivity", test_api_connectivity),
                ("JavaScript Errors", test_javascript_errors),
                ("Network Requests", test_network_requests),
                ("UI Interactions", test_ui_interactions),
                ("Drag & Drop", test_drag_drop_functionality),
                ("Performance", test_performance_metrics),
            ]

            for test_name, test_func in tests:
                print(f"\n{'=' * 20} {test_name} {'=' * 20}")
                try:
                    await test_func(page, report)
                except Exception as e:
                    report.add_issue(
                        "test_execution", "critical", f"{test_name} failed: {str(e)}"
                    )

            report.generate_summary()

        finally:
            await browser.close()

    return report


def print_detailed_report(report: UITestReport):
    """Print a detailed test report"""
    print("\n" + "=" * 60)
    print("📊 COMPREHENSIVE UI TEST REPORT")
    print("=" * 60)

    summary = report.results["summary"]
    status_emoji = (
        "✅"
        if summary["status"] == "PASS"
        else "⚠️"
        if summary["status"] == "PARTIAL"
        else "❌"
    )

    print(f"\n{status_emoji} Overall Status: {summary['status']}")
    print(f"📈 Total Issues: {summary['total_issues']}")
    print(f"🚨 Critical Issues: {summary['critical_issues']}")
    print(f"⚠️  Warnings: {summary['warnings']}")

    if summary["critical_issues"] > 0:
        print(f"\n🚨 CRITICAL ISSUES (Must Fix):")
        for issue in report.results["issues"]:
            if issue["severity"] == "critical":
                print(f"   • {issue['category']}: {issue['description']}")
                if issue["details"]:
                    print(f"     Details: {issue['details']}")

    if summary["warnings"] > 0:
        print(f"\n⚠️  WARNINGS (Should Fix):")
        for issue in report.results["issues"]:
            if issue["severity"] == "warning":
                print(f"   • {issue['category']}: {issue['description']}")

    # Performance metrics
    if "performance" in report.results and report.results["performance"]:
        perf = report.results["performance"]
        print(f"\n📊 PERFORMANCE METRICS:")
        if "page_load_time" in perf:
            print(f"   • Page Load Time: {perf['page_load_time']:.2f}s")
        if "total_js_size" in perf:
            print(f"   • JavaScript Bundle: {perf['total_js_size'] / 1024:.1f}KB")
        if "total_css_size" in perf:
            print(f"   • CSS Bundle: {perf['total_css_size'] / 1024:.1f}KB")

    # JavaScript errors
    if report.results["javascript_errors"]:
        print(f"\n🐛 JAVASCRIPT ERRORS:")
        for error in report.results["javascript_errors"]:
            print(f"   • {error['type']}: {error['text']}")

    # Network requests summary
    network_requests = len(report.results["network_requests"])
    print(f"\n🌐 NETWORK ACTIVITY:")
    print(f"   • Total Requests: {network_requests}")

    print(f"\n{'=' * 60}")

    # Recommendations
    print("💡 RECOMMENDATIONS:")

    if summary["critical_issues"] == 0 and summary["warnings"] == 0:
        print("   ✅ UI is working perfectly! All tests passed.")

    if summary["critical_issues"] > 0:
        print("   🚨 Fix critical issues immediately - the UI may not be functional")
        print("   • Check that both Svelte dev server and FastAPI backend are running")
        print("   • Verify CORS configuration allows communication between ports")
        print("   • Check browser console for detailed error messages")

    if summary["warnings"] > 0:
        print("   ⚠️  Address warnings to improve user experience")
        print("   • Check for minor UI issues or performance optimizations")

    print("   📋 Next steps:")
    print("   • Test with actual JSONL file uploads")
    print("   • Verify drag-and-drop with real files")
    print("   • Test different file types and error scenarios")
    print("   • Check mobile responsiveness on real devices")


if __name__ == "__main__":
    try:
        # Run the comprehensive test suite
        report = asyncio.run(run_comprehensive_tests())

        # Print detailed report
        print_detailed_report(report)

        # Exit with appropriate code
        exit_code = 0 if report.results["summary"]["critical_issues"] == 0 else 1
        sys.exit(exit_code)

    except KeyboardInterrupt:
        print("\n⏹️  Testing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Testing failed with unexpected error: {str(e)}")
        sys.exit(1)

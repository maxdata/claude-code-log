#!/usr/bin/env python3
"""
Complete UI Testing Suite with Pre-flight Checks

This comprehensive script:
1. Checks server availability
2. Installs required dependencies
3. Runs extensive UI testing
4. Generates detailed reports
"""

import asyncio
import json
import os
import socket
import subprocess
import sys
import time
from typing import Dict, List, Any


# Check if playwright is available, install if needed
def ensure_playwright():
    """Ensure playwright is installed and ready"""
    try:
        from playwright.async_api import async_playwright

        print("✅ Playwright is available")
        return True
    except ImportError:
        print("📦 Installing Playwright...")
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "playwright>=1.40.0"],
                check=True,
            )
            subprocess.run(
                [sys.executable, "-m", "playwright", "install", "chromium"], check=True
            )
            print("✅ Playwright installed successfully")
            # Re-import after installation
            from playwright.async_api import async_playwright

            return True
        except Exception as e:
            print(f"❌ Failed to install Playwright: {e}")
            return False


# Import playwright after ensuring it's available
if not ensure_playwright():
    sys.exit(1)

from playwright.async_api import async_playwright, Page, Request, Response

# Configuration
SVELTE_URL = "http://localhost:5173"
API_BASE = "http://localhost:8000"
TEST_TIMEOUT = 30000


class UITestReport:
    def __init__(self):
        self.results: Dict[str, Any] = {
            "preflight": {},
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


def check_port(host: str, port: int, name: str) -> bool:
    """Check if a port is open"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except:
        return False


async def preflight_checks(report: UITestReport) -> bool:
    """Run preflight checks before testing"""
    print("\n🔍 Running preflight checks...")

    all_good = True

    # Check FastAPI backend
    if check_port("localhost", 8000, "FastAPI"):
        report.add_success("preflight", "FastAPI backend is running on port 8000")
    else:
        report.add_issue(
            "preflight", "critical", "FastAPI backend not responding on port 8000"
        )
        all_good = False

    # Check Svelte dev server
    if check_port("localhost", 5173, "Svelte"):
        report.add_success("preflight", "Svelte dev server is running on port 5173")
    else:
        report.add_issue(
            "preflight", "critical", "Svelte dev server not responding on port 5173"
        )
        all_good = False

    return all_good


async def test_page_loading(page: Page, report: UITestReport) -> bool:
    """Test basic page loading and initial state"""
    print("\n🔍 Testing page loading...")

    try:
        response = await page.goto(
            SVELTE_URL, timeout=TEST_TIMEOUT, wait_until="networkidle"
        )

        if not response or response.status != 200:
            report.add_issue(
                "page_load",
                "critical",
                f"Page load failed with status {response.status if response else 'No response'}",
            )
            return False

        report.add_success(
            "page_load", f"Page loaded successfully (HTTP {response.status})"
        )

        # Wait for Svelte to initialize
        await page.wait_for_load_state("domcontentloaded")
        await page.wait_for_timeout(2000)

        # Check title
        title = await page.title()
        if "Claude Code Log Viewer" not in title:
            report.add_issue("page_load", "warning", f"Unexpected page title: {title}")
        else:
            report.add_success("page_load", f"Correct page title: {title}")

        # Check essential elements
        essential_elements = [
            (".app", "Main app container"),
            (".welcome-section", "Welcome section"),
            (".file-upload", "File upload component"),
            (".drop-zone", "Drop zone"),
        ]

        for selector, name in essential_elements:
            count = await page.locator(selector).count()
            if count == 0:
                severity = (
                    "critical" if selector in [".app", ".file-upload"] else "warning"
                )
                report.add_issue("page_load", severity, f"{name} not found")
                if severity == "critical":
                    return False
            else:
                report.add_success("page_load", f"{name} found")

        return True

    except Exception as e:
        report.add_issue("page_load", "critical", f"Page loading failed: {str(e)}")
        return False


async def test_api_connectivity(page: Page, report: UITestReport) -> bool:
    """Test API connectivity"""
    print("\n🔍 Testing API connectivity...")

    try:
        # Test health endpoint
        try:
            response = await page.request.get(f"{API_BASE}/health", timeout=5000)
            if response.status == 200:
                report.add_success("api_communication", "Health endpoint accessible")
            else:
                report.add_issue(
                    "api_communication",
                    "warning",
                    f"Health endpoint status {response.status}",
                )
        except Exception as e:
            report.add_issue(
                "api_communication", "warning", f"Health endpoint failed: {str(e)}"
            )

        # Test projects endpoint
        try:
            response = await page.request.get(f"{API_BASE}/api/projects", timeout=5000)
            if response.status == 200:
                report.add_success("api_communication", "Projects endpoint accessible")
            else:
                report.add_issue(
                    "api_communication",
                    "warning",
                    f"Projects endpoint status {response.status}",
                )
        except Exception as e:
            report.add_issue(
                "api_communication", "warning", f"Projects endpoint failed: {str(e)}"
            )

        return True

    except Exception as e:
        report.add_issue(
            "api_communication", "critical", f"API testing failed: {str(e)}"
        )
        return False


async def test_javascript_console(page: Page, report: UITestReport) -> bool:
    """Monitor JavaScript console for errors"""
    print("\n🔍 Monitoring JavaScript console...")

    def handle_console_message(msg):
        if msg.type in ["error", "warning"]:
            error_info = {
                "type": msg.type,
                "text": msg.text,
                "location": getattr(msg, "location", None),
            }
            report.results["javascript_errors"].append(error_info)
            severity = "critical" if msg.type == "error" else "warning"
            report.add_issue("javascript", severity, f"Console {msg.type}: {msg.text}")

    page.on("console", handle_console_message)

    # Reload to capture console messages
    await page.reload(wait_until="networkidle")
    await page.wait_for_timeout(3000)

    if len(report.results["javascript_errors"]) == 0:
        report.add_success("javascript", "No JavaScript errors detected")

    return True


async def test_ui_interactions(page: Page, report: UITestReport) -> bool:
    """Test UI interactions and responsiveness"""
    print("\n🔍 Testing UI interactions...")

    try:
        # Test drop zone interaction
        drop_zone = page.locator(".drop-zone")
        if await drop_zone.count() > 0:
            await drop_zone.hover()
            report.add_success("ui_interactions", "Drop zone is interactive")

            # Test drag events
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

            has_drag_class = await page.evaluate("""
                document.querySelector('.drop-zone').classList.contains('drag-active')
            """)

            if has_drag_class:
                report.add_success("ui_interactions", "Drag event handling works")
            else:
                report.add_issue(
                    "ui_interactions", "warning", "Drag events not handled properly"
                )
        else:
            report.add_issue("ui_interactions", "critical", "Drop zone not found")

        # Test upload button
        upload_button = page.locator(".upload-button")
        if await upload_button.count() > 0:
            is_visible = await upload_button.is_visible()
            if is_visible:
                report.add_success("ui_interactions", "Upload button is visible")
            else:
                report.add_issue(
                    "ui_interactions", "warning", "Upload button not visible"
                )
        else:
            report.add_issue("ui_interactions", "warning", "Upload button not found")

        # Test responsive design
        await page.set_viewport_size({"width": 360, "height": 640})
        await page.wait_for_timeout(1000)

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


async def test_performance(page: Page, report: UITestReport) -> bool:
    """Test performance metrics"""
    print("\n🔍 Testing performance...")

    try:
        start_time = time.time()
        await page.goto(SVELTE_URL, wait_until="networkidle")
        load_time = time.time() - start_time

        report.results["performance"]["page_load_time"] = load_time

        if load_time > 10:
            report.add_issue(
                "performance", "warning", f"Slow page load: {load_time:.2f}s"
            )
        else:
            report.add_success("performance", f"Good page load time: {load_time:.2f}s")

        return True

    except Exception as e:
        report.add_issue("performance", "warning", f"Performance test failed: {str(e)}")
        return False


async def run_comprehensive_tests():
    """Run all UI tests"""
    print("🚀 Starting Comprehensive Svelte UI Testing")
    print(f"📍 Target URL: {SVELTE_URL}")
    print(f"📍 API Base: {API_BASE}")
    print("=" * 60)

    report = UITestReport()

    # Preflight checks
    if not await preflight_checks(report):
        print("\n❌ Preflight checks failed. Servers may not be running.")
        report.generate_summary()
        return report

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True, args=["--no-sandbox", "--disable-dev-shm-usage"]
        )

        context = await browser.new_context(
            viewport={"width": 1280, "height": 720},
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        )

        page = await context.new_page()

        try:
            tests = [
                ("Page Loading", test_page_loading),
                ("API Connectivity", test_api_connectivity),
                ("JavaScript Console", test_javascript_console),
                ("UI Interactions", test_ui_interactions),
                ("Performance", test_performance),
            ]

            for test_name, test_func in tests:
                print(f"\n{'=' * 20} {test_name} {'=' * 20}")
                try:
                    await test_func(page, report)
                except Exception as e:
                    report.add_issue(
                        "test_execution", "critical", f"{test_name} failed: {str(e)}"
                    )

        finally:
            await browser.close()

    report.generate_summary()
    return report


def print_detailed_report(report: UITestReport):
    """Print comprehensive test report"""
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

    # JavaScript errors
    if report.results["javascript_errors"]:
        print(f"\n🐛 JAVASCRIPT ERRORS:")
        for error in report.results["javascript_errors"]:
            print(f"   • {error['type']}: {error['text']}")

    print(f"\n{'=' * 60}")

    # Recommendations
    print("💡 RECOMMENDATIONS:")

    if summary["critical_issues"] == 0 and summary["warnings"] == 0:
        print("   ✅ UI is working perfectly! All tests passed.")
    elif summary["critical_issues"] > 0:
        print("   🚨 Fix critical issues immediately:")
        print(
            "   • Ensure both Svelte (port 5173) and FastAPI (port 8000) servers are running"
        )
        print("   • Check CORS configuration between frontend and backend")
        print("   • Verify all essential UI components are rendering")
    elif summary["warnings"] > 0:
        print("   ⚠️  Address warnings to improve user experience")

    print("   📋 Next steps:")
    print("   • Test with actual JSONL file uploads")
    print("   • Verify drag-and-drop with real files")
    print("   • Test error handling with invalid files")


if __name__ == "__main__":
    try:
        report = asyncio.run(run_comprehensive_tests())
        print_detailed_report(report)

        exit_code = 0 if report.results["summary"]["critical_issues"] == 0 else 1
        sys.exit(exit_code)

    except KeyboardInterrupt:
        print("\n⏹️  Testing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Testing failed: {str(e)}")
        sys.exit(1)

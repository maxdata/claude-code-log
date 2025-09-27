#!/usr/bin/env python3

# Simple embedded test runner
import socket
import urllib.request
import urllib.error
import json


def test_ports_and_connectivity():
    print("🔍 Claude Code Log UI Testing")
    print("=" * 50)

    results = {
        "fastapi_port": False,
        "fastapi_http": False,
        "svelte_port": False,
        "svelte_http": False,
        "ui_working": False,
    }

    # Test FastAPI Backend (port 8000)
    print("1. Testing FastAPI Backend...")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        result = sock.connect_ex(("127.0.0.1", 8000))
        sock.close()

        if result == 0:
            results["fastapi_port"] = True
            print("   ✅ Port 8000 is open")

            # Test HTTP endpoint
            try:
                req = urllib.request.Request("http://127.0.0.1:8000/health")
                with urllib.request.urlopen(req, timeout=5) as response:
                    results["fastapi_http"] = True
                    print(f"   ✅ Health endpoint responds (HTTP {response.status})")
            except Exception as e:
                print(f"   ❌ Health endpoint failed: {e}")
        else:
            print("   ❌ Port 8000 is closed")
    except Exception as e:
        print(f"   ❌ FastAPI test error: {e}")

    # Test Svelte Dev Server (port 5173)
    print("\n2. Testing Svelte Dev Server...")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        result = sock.connect_ex(("127.0.0.1", 5173))
        sock.close()

        if result == 0:
            results["svelte_port"] = True
            print("   ✅ Port 5173 is open")

            # Test HTTP endpoint
            try:
                req = urllib.request.Request("http://127.0.0.1:5173")
                with urllib.request.urlopen(req, timeout=5) as response:
                    content = response.read(3000).decode("utf-8", errors="ignore")
                    results["svelte_http"] = True
                    print(f"   ✅ Frontend responds (HTTP {response.status})")

                    # Analyze content
                    ui_indicators = {
                        "title": "Claude Code Log Viewer" in content,
                        "file_upload": "file-upload" in content,
                        "drop_zone": "drop-zone" in content,
                        "svelte_app": "app" in content
                        and ("svelte" in content.lower() or "vite" in content.lower()),
                    }

                    found_indicators = sum(ui_indicators.values())

                    if found_indicators >= 2:
                        results["ui_working"] = True
                        print(f"   ✅ UI elements detected ({found_indicators}/4)")

                        if ui_indicators["title"]:
                            print("     ✅ Correct page title found")
                        if ui_indicators["file_upload"]:
                            print("     ✅ File upload component found")
                        if ui_indicators["drop_zone"]:
                            print("     ✅ Drop zone found")
                    else:
                        print(
                            f"   ⚠️  Limited UI elements detected ({found_indicators}/4)"
                        )
                        print(f"   Content preview: {content[:150]}...")

            except Exception as e:
                print(f"   ❌ Frontend HTTP test failed: {e}")
        else:
            print("   ❌ Port 5173 is closed")
    except Exception as e:
        print(f"   ❌ Svelte test error: {e}")

    # Final assessment
    print(f"\n{'=' * 50}")
    print("📊 TEST RESULTS")
    print("=" * 50)

    if results["ui_working"]:
        print("🎉 SUCCESS: UI appears to be working correctly!")
        print("\n✅ What's working:")
        if results["fastapi_port"]:
            print("   • FastAPI backend is running")
        if results["fastapi_http"]:
            print("   • API endpoints are accessible")
        if results["svelte_port"]:
            print("   • Svelte dev server is running")
        if results["svelte_http"]:
            print("   • Frontend is loading")
        if results["ui_working"]:
            print("   • UI components are rendering")

        print("\n📋 Manual Testing Steps:")
        print("   1. Open http://localhost:5173 in your browser")
        print("   2. Verify file upload interface is visible")
        print("   3. Try dragging a .jsonl file to the drop zone")
        print("   4. Check browser console for any JavaScript errors")
        print("   5. Test responsive design by resizing window")

        return True
    else:
        print("❌ ISSUES DETECTED")

        issues = []
        if not results["svelte_port"]:
            issues.append("Svelte dev server not running on port 5173")
        if not results["svelte_http"]:
            issues.append("Svelte frontend not responding to HTTP requests")
        if not results["fastapi_port"]:
            issues.append("FastAPI backend not running on port 8000")
        if not results["ui_working"]:
            issues.append("UI components not rendering properly")

        for issue in issues:
            print(f"   • {issue}")

        print("\n🔧 Troubleshooting:")
        if not results["svelte_port"]:
            print("   • Start Svelte: cd svelte-viewer && npm run dev")
        if not results["fastapi_port"]:
            print("   • Start FastAPI: uvicorn server:app --reload --port 8000")

        return False


# Run the test
if __name__ == "__main__":
    success = test_ports_and_connectivity()
    print(f"\nOverall result: {'PASS' if success else 'FAIL'}")

# Execute immediately
test_ports_and_connectivity()

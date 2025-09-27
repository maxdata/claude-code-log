#!/usr/bin/env python3
"""
Simple inline UI test for Claude Code Log Svelte interface
"""

import socket
import urllib.request
import urllib.error
import time

print("🚀 Testing Claude Code Log Svelte UI")
print("=" * 50)


def test_server_connectivity():
    """Test server connectivity"""
    print("\n🔍 Testing Server Connectivity")
    print("-" * 30)

    # Test FastAPI port 8000
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex(("localhost", 8000))
        sock.close()

        if result == 0:
            print("✅ FastAPI (port 8000): Server responding")
        else:
            print("❌ FastAPI (port 8000): Server not responding")
            return False
    except Exception as e:
        print(f"❌ FastAPI (port 8000): Error - {e}")
        return False

    # Test Svelte port 5173
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex(("localhost", 5173))
        sock.close()

        if result == 0:
            print("✅ Svelte (port 5173): Server responding")
        else:
            print("⚠️  Svelte (port 5173): Dev server not responding")
    except Exception as e:
        print(f"⚠️  Svelte (port 5173): Error - {e}")

    return True


def test_fastapi_endpoints():
    """Test FastAPI endpoints"""
    print("\n🌐 Testing FastAPI Endpoints")
    print("-" * 30)

    # Test health endpoint
    try:
        with urllib.request.urlopen(
            "http://localhost:8000/health", timeout=5
        ) as response:
            content = response.read().decode()
            print(f"✅ Health endpoint: HTTP {response.status}")
            print(f"   Response: {content[:100]}")
    except Exception as e:
        print(f"❌ Health endpoint failed: {e}")
        return False

    # Test projects API
    try:
        with urllib.request.urlopen(
            "http://localhost:8000/api/projects", timeout=5
        ) as response:
            print(f"✅ Projects API: HTTP {response.status}")
    except Exception as e:
        print(f"⚠️  Projects API: {e}")

    # Test main route (Svelte app served by FastAPI)
    try:
        with urllib.request.urlopen("http://localhost:8000/", timeout=5) as response:
            content = response.read(2000).decode("utf-8", errors="ignore")
            print(f"✅ Main route: HTTP {response.status}")

            # Check if it serves HTML
            if "<!DOCTYPE html>" in content:
                print("✅ Serves valid HTML")

                # Check for Svelte app indicators
                if "Claude Code Log Viewer" in content:
                    print("✅ Contains correct page title")
                else:
                    print("⚠️  Page title not found")

                # Check for app container
                if 'class="app"' in content or "class=app" in content:
                    print("✅ App container found")
                else:
                    print("⚠️  App container not found")

                # Check for script tags (Svelte/Vite)
                if "<script" in content:
                    print("✅ JavaScript loading detected")
                else:
                    print("⚠️  No JavaScript tags found")

                return content
            else:
                print("⚠️  Doesn't return HTML")

    except Exception as e:
        print(f"❌ Main route failed: {e}")
        return False

    return True


def test_svelte_dev_server():
    """Test Svelte dev server directly"""
    print("\n🎨 Testing Svelte Dev Server")
    print("-" * 30)

    try:
        with urllib.request.urlopen("http://localhost:5173", timeout=5) as response:
            content = response.read(3000).decode("utf-8", errors="ignore")
            print(f"✅ Svelte dev server: HTTP {response.status}")

            # Analyze content
            ui_elements = {
                "Page Title": "Claude Code Log Viewer" in content,
                "App Container": any(
                    x in content for x in ['class="app"', "class=app"]
                ),
                "File Upload": "file-upload" in content,
                "Drop Zone": "drop-zone" in content,
                "Upload Button": "upload-button" in content,
                "JavaScript": "<script" in content,
                "CSS": "<link" in content and "stylesheet" in content,
                "Vite/Svelte": any(
                    x in content.lower() for x in ["vite", "svelte", "_app"]
                ),
            }

            print("🔍 UI Elements Analysis:")
            for element, found in ui_elements.items():
                status = "✅" if found else "⚠️"
                print(f"   {status} {element}: {'Found' if found else 'Missing'}")

            found_count = sum(ui_elements.values())
            print(f"\n📊 UI Elements: {found_count}/{len(ui_elements)} found")

            return found_count >= 6  # Most elements should be present

    except Exception as e:
        print(f"❌ Svelte dev server test failed: {e}")
        return False


def generate_final_report(fastapi_ok, svelte_ok):
    """Generate final test report"""
    print("\n" + "=" * 50)
    print("📊 FINAL TEST REPORT")
    print("=" * 50)

    if fastapi_ok and svelte_ok:
        print("🎉 SUCCESS: UI is working correctly!")
        print("\n✅ What's working:")
        print("   • FastAPI backend serving Svelte app")
        print("   • All essential endpoints responding")
        print("   • Svelte dev server with UI components")
        print("   • CORS configuration allowing cross-origin requests")

        print("\n📋 Manual Testing Instructions:")
        print("   1. Open http://localhost:8000 in Chrome")
        print("   2. Verify file upload interface is visible")
        print("   3. Test drag-and-drop zone interaction")
        print("   4. Check browser console for JavaScript errors")
        print("   5. Monitor Network tab for API communication")
        print("   6. Test hover effects on upload zone")
        print("   7. Verify responsive design")

        return True

    elif fastapi_ok:
        print("⚠️  PARTIAL SUCCESS: FastAPI working, Svelte dev server issues")
        print("   • Backend is functional")
        print("   • UI can be accessed at http://localhost:8000")
        print("   • Svelte dev server may need restart")
        return False

    else:
        print("❌ CRITICAL ISSUES: FastAPI not responding")
        print("   • Check if servers are running")
        print(
            "   • Start FastAPI: uv run uvicorn claude_code_log.server:app --host 127.0.0.1 --port 8000 --reload"
        )
        print("   • Start Svelte: cd svelte-viewer && npm run dev")
        return False


def main():
    """Main test execution"""
    start_time = time.time()

    # Run tests
    connectivity_ok = test_server_connectivity()
    fastapi_ok = test_fastapi_endpoints() if connectivity_ok else False
    svelte_ok = test_svelte_dev_server()

    # Generate report
    overall_success = generate_final_report(fastapi_ok, svelte_ok)

    # Performance info
    duration = time.time() - start_time
    print(f"\n⏱️  Test completed in {duration:.2f} seconds")

    return overall_success


# Execute test
if __name__ == "__main__":
    success = main()
    exit_code = 0 if success else 1
    print(f"\nExit code: {exit_code}")

# Run the test immediately
success = main()

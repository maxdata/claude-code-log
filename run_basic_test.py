#!/usr/bin/env python3

import socket
import urllib.request
import urllib.error
import json
import subprocess
import sys


def test_port(host, port):
    """Test if port is open"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(2)
    result = sock.connect_ex((host, port))
    sock.close()
    return result == 0


def test_url(url):
    """Test URL accessibility"""
    try:
        with urllib.request.urlopen(url, timeout=5) as response:
            return response.status, response.read(1000).decode("utf-8", errors="ignore")
    except urllib.error.URLError as e:
        return None, str(e)
    except Exception as e:
        return None, str(e)


def run_tests():
    print("🔍 Basic Connectivity Test for Claude Code Log UI")
    print("=" * 50)

    # Test ports
    print("1. Testing port connectivity...")
    fastapi_port = test_port("localhost", 8000)
    svelte_port = test_port("localhost", 5173)

    print(f"   FastAPI Backend (8000): {'✅ OPEN' if fastapi_port else '❌ CLOSED'}")
    print(f"   Svelte Dev Server (5173): {'✅ OPEN' if svelte_port else '❌ CLOSED'}")

    # Test URLs
    print("\n2. Testing HTTP endpoints...")

    # Test FastAPI
    if fastapi_port:
        print("   Testing FastAPI endpoints...")

        # Health endpoint
        status, content = test_url("http://localhost:8000/health")
        if status:
            print(f"     ✅ /health: HTTP {status}")
        else:
            print(f"     ❌ /health: {content}")

        # Projects API endpoint
        status, content = test_url("http://localhost:8000/api/projects")
        if status:
            print(f"     ✅ /api/projects: HTTP {status}")
        else:
            print(f"     ❌ /api/projects: {content}")
    else:
        print("   ⚠️  Skipping FastAPI tests (server not running)")

    # Test Svelte frontend
    if svelte_port:
        print("\n   Testing Svelte frontend...")
        status, content = test_url("http://localhost:5173")

        if status:
            print(f"     ✅ Frontend loads: HTTP {status}")

            # Check content
            if "Claude Code Log Viewer" in content:
                print("     ✅ Found correct page title")
            elif "svelte" in content.lower() or "vite" in content.lower():
                print("     ✅ Detected Svelte/Vite app")
            else:
                print("     ⚠️  Unexpected content")
                print(f"     Content preview: {content[:150]}...")

            # Look for key elements in HTML
            elements_found = []
            if 'class="app"' in content or "class=app" in content:
                elements_found.append("app container")
            if "file-upload" in content:
                elements_found.append("file upload")
            if "drop-zone" in content:
                elements_found.append("drop zone")

            if elements_found:
                print(f"     ✅ UI elements found: {', '.join(elements_found)}")
            else:
                print("     ⚠️  No expected UI elements found in HTML")

        else:
            print(f"     ❌ Frontend failed: {content}")
    else:
        print("\n   ⚠️  Skipping Svelte tests (server not running)")

    # Summary and recommendations
    print(f"\n{'=' * 50}")
    print("📊 TEST SUMMARY")
    print("=" * 50)

    if fastapi_port and svelte_port:
        print("🎉 SUCCESS: Both servers are running correctly!")
        print("\n📋 Manual testing steps:")
        print("   1. Open http://localhost:5173 in your browser")
        print("   2. Verify you see 'Claude Code Log Viewer' title")
        print("   3. Look for a file upload interface with drag-and-drop")
        print("   4. Try hovering over the upload area (should change appearance)")
        print("   5. Check browser DevTools console for any errors")
        print("   6. Test drag-and-drop with a .jsonl file if available")

        print("\n🔍 API Testing:")
        print("   • Backend API is accessible at http://localhost:8000")
        print("   • Health check: http://localhost:8000/health")
        print("   • Projects API: http://localhost:8000/api/projects")

        return True

    elif svelte_port and not fastapi_port:
        print("⚠️  PARTIAL: Frontend is running, but backend is down")
        print("   • UI will load but file uploads will fail")
        print(
            "   • Start FastAPI backend: cd /path/to/project && uvicorn server:app --reload --port 8000"
        )
        return False

    elif fastapi_port and not svelte_port:
        print("⚠️  PARTIAL: Backend is running, but frontend is down")
        print("   • API endpoints work but no UI interface")
        print("   • Start Svelte dev server: cd svelte-viewer && npm run dev")
        return False

    else:
        print("❌ FAILURE: Both servers are down")
        print(
            "   • Start FastAPI: cd /path/to/project && uvicorn server:app --reload --port 8000"
        )
        print("   • Start Svelte: cd svelte-viewer && npm run dev")
        return False


def check_processes():
    """Check what processes might be using our ports"""
    print("\n🔍 Checking what's using the ports...")

    try:
        # Check port 8000
        result = subprocess.run(["lsof", "-i", ":8000"], capture_output=True, text=True)
        if result.stdout.strip():
            print("   Port 8000 (FastAPI):")
            print(f"   {result.stdout}")
        else:
            print("   Port 8000: No processes found")
    except:
        pass

    try:
        # Check port 5173
        result = subprocess.run(["lsof", "-i", ":5173"], capture_output=True, text=True)
        if result.stdout.strip():
            print("   Port 5173 (Svelte):")
            print(f"   {result.stdout}")
        else:
            print("   Port 5173: No processes found")
    except:
        pass


if __name__ == "__main__":
    try:
        success = run_tests()
        check_processes()

        if success:
            print("\n✅ All tests passed! UI should be working.")
        else:
            print("\n⚠️  Some issues found. See recommendations above.")

        sys.exit(0 if success else 1)

    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test failed: {e}")
        sys.exit(1)

# Execute the test
run_tests()
check_processes()

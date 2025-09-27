#!/usr/bin/env python3
"""
Quick UI Test - Simple check without heavy dependencies
"""

import requests
import socket
import time


def check_port(host, port, name):
    """Check if a port is open"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex((host, port))
        sock.close()

        if result == 0:
            print(f"✅ {name} is running on port {port}")
            return True
        else:
            print(f"❌ {name} is NOT running on port {port}")
            return False
    except Exception as e:
        print(f"❌ {name} port check failed: {e}")
        return False


def check_http(url, name):
    """Check HTTP endpoint"""
    try:
        response = requests.get(url, timeout=5)
        print(f"✅ {name} responds with HTTP {response.status_code}: {url}")
        return response.status_code < 400
    except requests.exceptions.ConnectionError:
        print(f"❌ {name} connection refused: {url}")
        return False
    except requests.exceptions.Timeout:
        print(f"❌ {name} timeout: {url}")
        return False
    except Exception as e:
        print(f"❌ {name} error: {e}")
        return False


def main():
    print("🔍 Quick Server Health Check")
    print("=" * 40)

    # Check ports
    fastapi_ok = check_port("localhost", 8000, "FastAPI Backend")
    svelte_ok = check_port("localhost", 5173, "Svelte Dev Server")

    print()

    # Check HTTP if ports are open
    if fastapi_ok:
        check_http("http://localhost:8000/health", "FastAPI Health")
        check_http("http://localhost:8000/api/projects", "FastAPI Projects API")

    if svelte_ok:
        check_http("http://localhost:5173", "Svelte Frontend")

    print("\n" + "=" * 40)

    if fastapi_ok and svelte_ok:
        print("🎉 Both servers are running! UI should be working.")

        print("\n📋 Manual Testing Steps:")
        print("1. Open http://localhost:5173 in your browser")
        print("2. Check for 'Claude Code Log Viewer' title")
        print("3. Look for file upload interface with drag-and-drop zone")
        print("4. Try hovering over the upload area")
        print("5. Check browser console for any JavaScript errors")
        print("6. Test responsiveness by resizing browser window")

        return True
    else:
        print("⚠️  Some servers are not running. Please start them first:")

        if not fastapi_ok:
            print(
                "   • FastAPI Backend: cd /path/to/project && uvicorn server:app --reload --port 8000"
            )

        if not svelte_ok:
            print("   • Svelte Dev Server: cd svelte-viewer && npm run dev")

        return False


if __name__ == "__main__":
    main()

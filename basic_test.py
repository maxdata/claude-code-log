#!/usr/bin/env python3

import socket
import urllib.request
import urllib.error


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


print("🔍 Basic Connectivity Test")
print("=" * 30)

# Test ports
print("Testing ports...")
fastapi_port = test_port("localhost", 8000)
svelte_port = test_port("localhost", 5173)

print(f"FastAPI (8000): {'✅ OPEN' if fastapi_port else '❌ CLOSED'}")
print(f"Svelte (5173): {'✅ OPEN' if svelte_port else '❌ CLOSED'}")

print("\nTesting URLs...")

if fastapi_port:
    status, content = test_url("http://localhost:8000/health")
    print(
        f"FastAPI Health: {'✅ OK' if status else '❌ FAIL'} {status or content[:100]}"
    )

if svelte_port:
    status, content = test_url("http://localhost:5173")
    print(
        f"Svelte Frontend: {'✅ OK' if status else '❌ FAIL'} {status or content[:100]}"
    )
    if status and content:
        # Check if it looks like a Svelte app
        if "Claude Code Log Viewer" in content:
            print("✅ Found Claude Code Log Viewer title in response")
        elif "svelte" in content.lower() or "vite" in content.lower():
            print("✅ Looks like a Svelte/Vite app")
        else:
            print("⚠️  Response doesn't look like expected Svelte app")
            print(f"Content preview: {content[:200]}")

print(f"\n{'=' * 30}")
if fastapi_port and svelte_port:
    print("🎉 Both servers are running!")
    print("\nTo test manually:")
    print("1. Open http://localhost:5173 in your browser")
    print("2. Look for file upload interface")
    print("3. Try dragging files to the drop zone")
elif svelte_port:
    print("✅ Svelte is running, but FastAPI is down")
    print("   UI will load but API calls will fail")
elif fastapi_port:
    print("✅ FastAPI is running, but Svelte is down")
    print("   Backend works but no frontend")
else:
    print("❌ Both servers are down")

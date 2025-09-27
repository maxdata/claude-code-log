#!/usr/bin/env python3

import socket
import urllib.request
import urllib.error
import subprocess
import sys
import time


# Run the test directly without executing external files
def test_connectivity():
    print("🔍 Direct Connectivity Test")
    print("=" * 40)

    # Test port 8000 (FastAPI)
    print("Testing FastAPI Backend (port 8000)...")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex(("localhost", 8000))
        sock.close()

        if result == 0:
            print("✅ FastAPI port 8000 is OPEN")

            # Test HTTP
            try:
                with urllib.request.urlopen(
                    "http://localhost:8000/health", timeout=5
                ) as response:
                    content = response.read().decode()
                    print(f"✅ FastAPI health endpoint responds: {response.status}")
                    print(f"   Response: {content[:100]}")
            except Exception as e:
                print(f"❌ FastAPI HTTP test failed: {e}")

        else:
            print("❌ FastAPI port 8000 is CLOSED")
    except Exception as e:
        print(f"❌ FastAPI port test error: {e}")

    print()

    # Test port 5173 (Svelte)
    print("Testing Svelte Dev Server (port 5173)...")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex(("localhost", 5173))
        sock.close()

        if result == 0:
            print("✅ Svelte port 5173 is OPEN")

            # Test HTTP
            try:
                with urllib.request.urlopen(
                    "http://localhost:5173", timeout=5
                ) as response:
                    content = response.read(2000).decode("utf-8", errors="ignore")
                    print(f"✅ Svelte frontend responds: {response.status}")

                    # Check for expected content
                    if "Claude Code Log Viewer" in content:
                        print("✅ Found 'Claude Code Log Viewer' in page")
                    else:
                        print("⚠️  'Claude Code Log Viewer' not found in page")

                    if "file-upload" in content or "drop-zone" in content:
                        print("✅ Found file upload elements")
                    else:
                        print("⚠️  File upload elements not found")

                    print(f"   Content preview: {content[:200]}...")

            except Exception as e:
                print(f"❌ Svelte HTTP test failed: {e}")

        else:
            print("❌ Svelte port 5173 is CLOSED")
    except Exception as e:
        print(f"❌ Svelte port test error: {e}")

    # Summary
    print(f"\n{'=' * 40}")
    print("Summary: Open http://localhost:5173 in your browser to test manually")
    print("Expected: File upload interface with drag-and-drop functionality")


if __name__ == "__main__":
    test_connectivity()

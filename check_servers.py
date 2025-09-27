#!/usr/bin/env python3
"""
Quick server health check before running UI tests
"""

import requests
import socket
import sys


def check_port(host, port, name):
    """Check if a port is open and responsive"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex((host, port))
        sock.close()

        if result == 0:
            print(f"✅ {name} port {port} is open")
            return True
        else:
            print(f"❌ {name} port {port} is closed")
            return False
    except Exception as e:
        print(f"❌ {name} port check failed: {e}")
        return False


def check_http_endpoint(url, name):
    """Check if HTTP endpoint is responsive"""
    try:
        response = requests.get(url, timeout=5)
        print(f"✅ {name} HTTP {response.status_code}: {url}")
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
    print("🔍 Checking server status before UI testing...")
    print("=" * 50)

    all_good = True

    # Check ports
    if not check_port("localhost", 8000, "FastAPI Backend"):
        all_good = False

    if not check_port("localhost", 5173, "Svelte Dev Server"):
        all_good = False

    print()

    # Check HTTP endpoints
    if not check_http_endpoint("http://localhost:8000/health", "FastAPI Health"):
        all_good = False

    if not check_http_endpoint("http://localhost:5173", "Svelte Frontend"):
        all_good = False

    print()

    if all_good:
        print("🎉 All servers are running! Ready for UI testing.")
        return True
    else:
        print("⚠️  Some servers are not responding. UI tests may fail.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

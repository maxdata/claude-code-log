#!/usr/bin/env python3

import urllib.request
import urllib.error

print("🔍 Quick Endpoint Validation")
print("=" * 30)

# Test the main endpoints
endpoints = [
    ("http://localhost:8000/health", "FastAPI Health"),
    ("http://localhost:8000/api/projects", "Projects API"),
    ("http://localhost:8000/", "Main Route (Svelte App)"),
    ("http://localhost:5173", "Svelte Dev Server"),
]

for url, name in endpoints:
    try:
        with urllib.request.urlopen(url, timeout=3) as response:
            content = response.read(500).decode("utf-8", errors="ignore")
            print(f"✅ {name}: HTTP {response.status}")

            # Special checks
            if "health" in url and "healthy" in content:
                print("   • Health status: OK")
            elif url.endswith("/"):
                if "<!DOCTYPE html>" in content:
                    print("   • HTML document detected")
                if "Claude Code Log Viewer" in content:
                    print("   • Correct page title found")
                if "app" in content.lower():
                    print("   • App structure detected")

    except urllib.error.URLError as e:
        print(f"❌ {name}: Connection failed - {e}")
    except Exception as e:
        print(f"❌ {name}: Error - {e}")

print("\n" + "=" * 30)
print("Validation complete")

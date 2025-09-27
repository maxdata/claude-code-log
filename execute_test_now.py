#!/usr/bin/env python3

# Execute the comprehensive UI test immediately
import subprocess
import sys
import os

os.chdir("/Users/max/Documents/GitHub/claude-code-log")

try:
    result = subprocess.run(
        [sys.executable, "run_comprehensive_ui_test.py"],
        capture_output=False,
        text=True,
    )
    sys.exit(result.returncode)
except Exception as e:
    print(f"Failed to run test: {e}")
    sys.exit(1)

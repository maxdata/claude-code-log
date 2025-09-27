#!/bin/bash

# UI Testing Script for Claude Code Log Svelte Viewer
# This script installs dependencies and runs comprehensive UI testing

set -e

echo "🚀 Setting up UI Testing Environment..."

# Change to svelte-viewer directory
cd /Users/max/Documents/GitHub/claude-code-log/svelte-viewer

# Install playwright if not already installed
echo "📦 Installing Playwright..."
pip install playwright==1.40.0

# Install browser dependencies
echo "🌐 Installing Chromium browser..."
playwright install chromium

# Run the comprehensive UI test
echo "🧪 Running Comprehensive UI Tests..."
echo "======================================"

python test_ui.py
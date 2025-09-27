#!/bin/bash
# UI Functionality Test Script for FastAPI + Svelte App
# Tests all key endpoints and provides comprehensive validation

echo "=== FastAPI + Svelte UI Test Report ==="
echo "Testing Date: $(date)"
echo ""

# Test 1: Health Check Endpoint
echo "1. Testing Health Check Endpoint..."
echo "GET http://localhost:8000/health"
HEALTH_RESPONSE=$(curl -s -w "HTTPSTATUS:%{http_code};TIME:%{time_total}" http://localhost:8000/health)
HEALTH_STATUS=$(echo $HEALTH_RESPONSE | grep -o "HTTPSTATUS:[0-9]*" | cut -d: -f2)
HEALTH_TIME=$(echo $HEALTH_RESPONSE | grep -o "TIME:[0-9.]*" | cut -d: -f2)
HEALTH_BODY=$(echo $HEALTH_RESPONSE | sed 's/HTTPSTATUS:[0-9]*;TIME:[0-9.]*//')

echo "Status Code: $HEALTH_STATUS"
echo "Response Time: ${HEALTH_TIME}s"
echo "Response Body: $HEALTH_BODY"
echo ""

# Test 2: Main Page (Svelte App)
echo "2. Testing Main Page (Svelte App)..."
echo "GET http://localhost:8000/"
MAIN_RESPONSE=$(curl -s -w "HTTPSTATUS:%{http_code};TIME:%{time_total}" http://localhost:8000/)
MAIN_STATUS=$(echo $MAIN_RESPONSE | grep -o "HTTPSTATUS:[0-9]*" | cut -d: -f2)
MAIN_TIME=$(echo $MAIN_RESPONSE | grep -o "TIME:[0-9.]*" | cut -d: -f2)
MAIN_BODY=$(echo $MAIN_RESPONSE | sed 's/HTTPSTATUS:[0-9]*;TIME:[0-9.]*//')

echo "Status Code: $MAIN_STATUS"
echo "Response Time: ${MAIN_TIME}s"
echo "Content-Type: $(curl -s -I http://localhost:8000/ | grep -i content-type)"
echo "Content Length: $(echo "$MAIN_BODY" | wc -c) characters"

# Check for key HTML elements
echo ""
echo "HTML Content Analysis:"
if echo "$MAIN_BODY" | grep -q "<!DOCTYPE html>"; then
    echo "✓ Valid HTML document detected"
else
    echo "✗ Missing DOCTYPE declaration"
fi

if echo "$MAIN_BODY" | grep -q '<div id="app">'; then
    echo "✓ Svelte app container found"
else
    echo "✗ Missing Svelte app container"
fi

if echo "$MAIN_BODY" | grep -q 'vite'; then
    echo "✓ Vite build artifacts detected"
else
    echo "✗ Missing Vite build artifacts"
fi

echo ""

# Test 3: Projects API Endpoint
echo "3. Testing Projects API Endpoint..."
echo "GET http://localhost:8000/api/projects"
PROJECTS_RESPONSE=$(curl -s -w "HTTPSTATUS:%{http_code};TIME:%{time_total}" http://localhost:8000/api/projects)
PROJECTS_STATUS=$(echo $PROJECTS_RESPONSE | grep -o "HTTPSTATUS:[0-9]*" | cut -d: -f2)
PROJECTS_TIME=$(echo $PROJECTS_RESPONSE | grep -o "TIME:[0-9.]*" | cut -d: -f2)
PROJECTS_BODY=$(echo $PROJECTS_RESPONSE | sed 's/HTTPSTATUS:[0-9]*;TIME:[0-9.]*//')

echo "Status Code: $PROJECTS_STATUS"
echo "Response Time: ${PROJECTS_TIME}s"
echo "Response Body Preview: $(echo "$PROJECTS_BODY" | head -c 200)..."
echo ""

# Test 4: Static Assets
echo "4. Testing Static Assets..."
# Test for common Svelte/Vite assets
for asset in "assets/index.js" "assets/index.css" "favicon.ico"; do
    echo "Testing /static/$asset"
    ASSET_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:8000/static/$asset")
    echo "Status: $ASSET_STATUS"
done
echo ""

# Test 5: CORS Headers
echo "5. Testing CORS Configuration..."
CORS_RESPONSE=$(curl -s -I -H "Origin: http://localhost:5173" http://localhost:8000/api/projects)
echo "CORS Headers:"
echo "$CORS_RESPONSE" | grep -i "access-control-allow"
echo ""

# Test 6: WebSocket Support (if any)
echo "6. Testing WebSocket Support..."
WS_RESPONSE=$(curl -s -I -H "Connection: Upgrade" -H "Upgrade: websocket" http://localhost:8000/)
WS_STATUS=$(echo "$WS_RESPONSE" | head -1 | grep -o "[0-9][0-9][0-9]")
echo "WebSocket Upgrade Status: $WS_STATUS"
echo ""

# Summary
echo "=== Test Summary ==="
if [ "$HEALTH_STATUS" = "200" ] && [ "$MAIN_STATUS" = "200" ] && [ "$PROJECTS_STATUS" = "200" ]; then
    echo "✓ All critical endpoints responding correctly"
    echo "✓ FastAPI server serving Svelte app successfully"
    echo "✓ API endpoints accessible and functional"
else
    echo "✗ Some endpoints failing - check individual test results above"
fi

echo ""
echo "Performance Summary:"
echo "Health Check: ${HEALTH_TIME}s"
echo "Main Page Load: ${MAIN_TIME}s"
echo "Projects API: ${PROJECTS_TIME}s"

echo ""
echo "=== Manual UI Testing Instructions ==="
echo "Open Chrome and navigate to: http://localhost:8000"
echo ""
echo "1. Verify UI Components:"
echo "   - Look for main app container with class 'app'"
echo "   - Check welcome section with file upload interface"
echo "   - Verify FileUpload component with drag-and-drop zone"
echo "   - Confirm upload button and file selection are visible"
echo ""
echo "2. Test Interactions:"
echo "   - Hover over upload zone (should show visual feedback)"
echo "   - Try drag-and-drop functionality"
echo "   - Click upload button to test file selection"
echo ""
echo "3. Developer Tools Checks:"
echo "   - Open Chrome DevTools (F12)"
echo "   - Check Console tab for JavaScript errors"
echo "   - Monitor Network tab for failed requests"
echo "   - Verify all static assets load successfully"
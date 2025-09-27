#!/bin/bash

# Execute comprehensive UI test and display results
echo "🚀 Executing Comprehensive UI Test for Claude Code Log"
echo "======================================================"

cd /Users/max/Documents/GitHub/claude-code-log

# Run the comprehensive test
python3 run_comprehensive_ui_test.py

exit_code=$?
echo ""
echo "Test execution completed with exit code: $exit_code"

if [ $exit_code -eq 0 ]; then
    echo "✅ All tests passed! UI is working correctly."
else
    echo "⚠️ Some issues detected. Review the report above."
fi
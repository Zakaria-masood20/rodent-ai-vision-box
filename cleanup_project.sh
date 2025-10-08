#!/bin/bash

# Cleanup Script for Rodent Detection System
# This script organizes the project for production deployment

echo "================================"
echo "🧹 CLEANING PROJECT STRUCTURE"
echo "================================"

# Create archive directory for test files
echo "📁 Creating archive directory..."
mkdir -p archive/test_scripts
mkdir -p archive/test_results
mkdir -p archive/test_reports

# Move test scripts to archive
echo "📦 Archiving test scripts..."
mv -f corrected_video_test.py archive/test_scripts/ 2>/dev/null
mv -f debug_video_test.py archive/test_scripts/ 2>/dev/null
mv -f fixed_video_test.py archive/test_scripts/ 2>/dev/null
mv -f quick_video_test.py archive/test_scripts/ 2>/dev/null
mv -f run_video_test.py archive/test_scripts/ 2>/dev/null
mv -f simple_video_test.py archive/test_scripts/ 2>/dev/null
mv -f test_detection_with_email.py archive/test_scripts/ 2>/dev/null
mv -f test_real_detection_email.py archive/test_scripts/ 2>/dev/null
mv -f test_video_detection.py archive/test_scripts/ 2>/dev/null
mv -f test_videos.py archive/test_scripts/ 2>/dev/null
mv -f test_whatsapp.py archive/test_scripts/ 2>/dev/null

# Move test results
echo "📊 Archiving test results..."
mv -f test_results/* archive/test_results/ 2>/dev/null

# Move test reports
echo "📄 Archiving test reports..."
mv -f TEST_RESULTS_SUMMARY.md archive/test_reports/ 2>/dev/null
mv -f FINAL_TEST_RESULTS.md archive/test_reports/ 2>/dev/null

# Keep only essential test files
echo "✅ Keeping essential test files..."
# Keep test_emailjs.py and test_detection.py as they're needed for verification

# Remove Python cache
echo "🗑️  Removing Python cache..."
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -delete 2>/dev/null

# Remove test environment (can be recreated)
echo "🗑️  Removing test environment..."
rm -rf test_env

# Clean up data directories
echo "🧹 Cleaning data directories..."
mkdir -p data/logs
mkdir -p data/images
mkdir -p data/detections
rm -f data/logs/*.log 2>/dev/null

# Organize documentation
echo "📚 Organizing documentation..."
mkdir -p docs/archive
mv -f fix_sms.md docs/archive/ 2>/dev/null
mv -f urgent_message_to_david.txt archive/ 2>/dev/null
mv -f email_to_david.txt archive/ 2>/dev/null

# Create clean project structure
echo "🏗️  Creating clean structure..."

# Main directories that should exist
mkdir -p src
mkdir -p config
mkdir -p models
mkdir -p scripts
mkdir -p data/logs
mkdir -p data/images
mkdir -p docs

# List final structure
echo ""
echo "================================"
echo "✅ CLEANUP COMPLETE"
echo "================================"
echo ""
echo "📁 Final Structure:"
echo ""
tree -L 2 -I 'archive|__pycache__|*.pyc' 2>/dev/null || ls -la

echo ""
echo "📦 Archived files are in: ./archive/"
echo "🚀 Project is now clean and ready for production!"
echo ""
echo "Next steps:"
echo "1. Review the clean structure"
echo "2. Test core functionality"
echo "3. Deploy to Raspberry Pi"
echo "================================"
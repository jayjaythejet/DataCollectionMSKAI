#!/usr/bin/env bash
# Build script for MSK Data Collector
# Run this on the target platform (Mac or Windows).
# Requires: pip install pyinstaller

set -e

echo "Installing dependencies..."
pip3 install customtkinter openpyxl pyperclip pyinstaller

echo "Building application..."
pyinstaller \
  --onefile \
  --windowed \
  --name "MSK_DataCollector" \
  --add-data "ui:ui" \
  --add-data "data:data" \
  --add-data "utils:utils" \
  app.py

echo ""
echo "Build complete!"
echo "  Mac:     dist/MSK_DataCollector.app"
echo "  Windows: dist/MSK_DataCollector.exe"

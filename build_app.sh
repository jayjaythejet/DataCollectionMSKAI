#!/usr/bin/env bash
# Build script for MSK Data Collector
# Run this on the target platform (Mac or Windows).
# Requires: pip install pyinstaller

set -e

# PyInstaller uses ':' on Mac/Linux and ';' on Windows
SEP=$(python3 -c "import os; print(os.pathsep)")

echo "Installing dependencies..."
pip3 install customtkinter openpyxl xlrd pyperclip platformdirs pyinstaller

echo "Cleaning previous build artifacts..."
rm -rf dist build MSK_DataCollector.spec

echo "Building application..."
pyinstaller \
  --onefile \
  --windowed \
  --clean \
  --name "MSK_DataCollector" \
  --hidden-import=xlrd \
  --add-data "ui${SEP}ui" \
  --add-data "data${SEP}data" \
  --add-data "utils${SEP}utils" \
  app.py

echo ""
echo "Build complete!"
echo "  Mac:     dist/MSK_DataCollector.app"
echo "  Windows: dist/MSK_DataCollector.exe"

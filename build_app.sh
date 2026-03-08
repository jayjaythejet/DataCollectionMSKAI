#!/usr/bin/env bash
# Build script for MSK Data Collector (Knee + Shoulder)
# Run this on the target platform (Mac or Windows).
# Requires: pip install pyinstaller

set -e

# PyInstaller uses ':' on Mac/Linux and ';' on Windows
SEP=$(python3 -c "import os; print(os.pathsep)")

echo "Installing dependencies..."
pip3 install customtkinter openpyxl xlrd pyperclip platformdirs pyinstaller

echo "Cleaning previous build artifacts..."
rm -rf dist build *.spec

echo "Building Knee application..."
pyinstaller \
  --onefile \
  --windowed \
  --clean \
  --name "MSK_Knee_DataCollector" \
  --hidden-import=xlrd \
  --add-data "ui${SEP}ui" \
  --add-data "data${SEP}data" \
  --add-data "utils${SEP}utils" \
  --add-data "configs${SEP}configs" \
  app_knee.py

echo "Building Shoulder application..."
pyinstaller \
  --onefile \
  --windowed \
  --clean \
  --name "MSK_Shoulder_DataCollector" \
  --hidden-import=xlrd \
  --add-data "ui${SEP}ui" \
  --add-data "data${SEP}data" \
  --add-data "utils${SEP}utils" \
  --add-data "configs${SEP}configs" \
  app_shoulder.py

echo ""
echo "Build complete!"
echo "  Knee:     dist/MSK_Knee_DataCollector"
echo "  Shoulder: dist/MSK_Shoulder_DataCollector"

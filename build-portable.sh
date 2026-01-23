#!/bin/bash
# Build script for RePhraser portable executable

echo "Building RePhraser portable executable..."

# Check if PyInstaller is installed
if ! command -v pyinstaller &> /dev/null; then
    echo "PyInstaller not found. Installing..."
    pip install pyinstaller
fi

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf build/ dist/

# Build using the spec file
echo "Building executable..."
pyinstaller rephraser.spec

# Check if build was successful
if [ -f "dist/RePhraser-Portable" ] || [ -f "dist/RePhraser-Portable.exe" ]; then
    echo "✓ Build successful!"
    echo "Executable created in dist/ folder"
    ls -la dist/
else
    echo "✗ Build failed!"
    exit 1
fi
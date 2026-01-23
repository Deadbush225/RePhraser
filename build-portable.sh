#!/bin/bash
# Build script for RePhraser portable executable

set -e  # Exit on any error

echo "Building RePhraser portable executable for Linux..."

# Check if PyInstaller is installed
if ! command -v pyinstaller &> /dev/null; then
    echo "PyInstaller not found. Installing..."
    pip install pyinstaller
fi

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf build/ dist/

# Set up virtual display if running in headless environment
if [ -z "$DISPLAY" ]; then
    echo "Setting up virtual display..."
    export DISPLAY=:99
    export QT_QPA_PLATFORM=offscreen
    if command -v Xvfb &> /dev/null; then
        Xvfb :99 -screen 0 1024x768x24 > /dev/null 2>&1 &
        sleep 2
    fi
fi

# Build using the spec file or direct command
echo "Building executable..."
if [ -f "rephraser.spec" ]; then
    pyinstaller rephraser.spec --noconfirm
else
    pyinstaller --name "rephraser" \
        --windowed \
        --onefile \
        --icon "src/rephraser/Rephraser.ico" \
        --add-data "src/rephraser/dark.qss:rephraser" \
        --add-data "src/rephraser/login.qss:rephraser" \
        --add-data "src/rephraser/Rephraser.ico:rephraser" \
        --add-data "src/rephraser/Rephraser.png:rephraser" \
        --add-data "src/rephraser/images:rephraser/images" \
        --hidden-import "PyQt5.sip" \
        --collect-all "PyQt5" \
        --clean \
        --noconfirm \
        src/rephraser/__main__.py
fi

# Check if build was successful and rename if needed
if [ -f "dist/rephraser" ]; then
    echo "✓ Build successful!"
    
    # Rename with version if VERSION environment variable is set
    if [ -n "$VERSION" ]; then
        mv "dist/rephraser" "dist/RePhraser-${VERSION}-Linux-x64-Portable"
        chmod +x "dist/RePhraser-${VERSION}-Linux-x64-Portable"
        echo "Renamed to: RePhraser-${VERSION}-Linux-x64-Portable"
    else
        chmod +x "dist/rephraser"
        echo "Executable created: dist/rephraser"
    fi
    
    echo "Build completed successfully!"
    ls -la dist/
elif [ -f "dist/RePhraser-Portable" ]; then
    echo "✓ Build successful!"
    if [ -n "$VERSION" ]; then
        mv "dist/RePhraser-Portable" "dist/RePhraser-${VERSION}-Linux-x64-Portable"
        chmod +x "dist/RePhraser-${VERSION}-Linux-x64-Portable"
        echo "Renamed to: RePhraser-${VERSION}-Linux-x64-Portable"
    fi
    echo "Build completed successfully!"
    ls -la dist/
else
    echo "✗ Build failed!"
    exit 1
fi
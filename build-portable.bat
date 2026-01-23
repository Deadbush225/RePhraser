@echo off
REM Build script for RePhraser portable executable on Windows

echo Building RePhraser portable executable...

REM Check if PyInstaller is installed
pip show pyinstaller >nul 2>&1
if %errorlevel% neq 0 (
    echo PyInstaller not found. Installing...
    pip install pyinstaller
)

REM Clean previous builds
echo Cleaning previous builds...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

REM Build using the spec file
echo Building executable...
pyinstaller rephraser.spec

REM Check if build was successful
if exist "dist\RePhraser-Portable.exe" (
    echo ✓ Build successful!
    echo Executable created in dist\ folder
    dir dist\
) else (
    echo ✗ Build failed!
    pause
    exit /b 1
)

pause
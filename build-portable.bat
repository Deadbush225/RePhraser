@echo off
REM Build script for RePhraser portable executable on Windows

echo Building RePhraser portable executable for Windows...

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

REM Build using the spec file or direct command
echo Building executable...
if exist "rephraser.spec" (
    pyinstaller rephraser.spec --noconfirm
) else (
    pyinstaller --name "RePhraser" ^
        --windowed ^
        --onefile ^
        --icon "src/rephraser/Rephraser.ico" ^
        --add-data "src/rephraser/dark.qss;rephraser" ^
        --add-data "src/rephraser/login.qss;rephraser" ^
        --add-data "src/rephraser/Rephraser.ico;rephraser" ^
        --add-data "src/rephraser/Rephraser.png;rephraser" ^
        --add-data "src/rephraser/images;rephraser/images" ^
        --hidden-import "PyQt5.sip" ^
        --clean ^
        --noconfirm ^
        src/rephraser/__main__.py
)

REM Check if build was successful and rename if needed
if exist "dist\RePhraser.exe" (
    echo ✓ Build successful!
    
    REM Rename with version if VERSION environment variable is set
    if defined VERSION (
        move "dist\RePhraser.exe" "dist\RePhraser-%VERSION%-Windows-x64-Portable.exe"
        echo Renamed to: RePhraser-%VERSION%-Windows-x64-Portable.exe
    ) else (
        echo Executable created: dist\RePhraser.exe
    )
    
    echo Build completed successfully!
    dir dist\
) else if exist "dist\RePhraser-Portable.exe" (
    echo ✓ Build successful!
    if defined VERSION (
        move "dist\RePhraser-Portable.exe" "dist\RePhraser-%VERSION%-Windows-x64-Portable.exe"
        echo Renamed to: RePhraser-%VERSION%-Windows-x64-Portable.exe
    )
    echo Build completed successfully!
    dir dist\
) else (
    echo ✗ Build failed!
    if not "%1"=="--no-pause" pause
    exit /b 1
)

if not "%1"=="--no-pause" pause
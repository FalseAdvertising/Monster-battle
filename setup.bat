@echo off
echo ========================================
echo Monster Battle - Setup & Installation
echo ========================================
echo.
echo This script will install the required dependencies for Monster Battle
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python is not installed or not in PATH
    echo.
    echo Please install Python from: https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

echo ✅ Python is installed
python --version

echo.
echo Installing pygame...
echo.

REM Try to install pygame
python -m pip install pygame

if %errorlevel% neq 0 (
    echo.
    echo ❌ Failed to install pygame with pip
    echo Trying alternative installation methods...
    echo.
    
    REM Try upgrading pip first
    echo Upgrading pip...
    python -m pip install --upgrade pip
    
    REM Try again
    echo Retrying pygame installation...
    python -m pip install pygame
    
    if %errorlevel% neq 0 (
        echo.
        echo ❌ Still failed to install pygame
        echo.
        echo Please try manual installation:
        echo 1. Open Command Prompt as Administrator
        echo 2. Run: python -m pip install pygame
        echo.
        pause
        exit /b 1
    )
)

echo.
echo ✅ pygame installed successfully!
echo.

REM Test pygame installation
echo Testing pygame installation...
python -c "import pygame; print('✅ pygame works!'); print(f'Version: {pygame.version.ver}')" 2>nul

if %errorlevel% neq 0 (
    echo ❌ pygame installation test failed
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================
echo 🎮 Monster Battle Setup Complete!
echo ========================================
echo.
echo You can now run the game using:
echo - start_game.bat (for the main menu)
echo - Or directly run specific components
echo.
echo For network play:
echo 1. Host: Choose option 1 to start server
echo 2. Guest: Choose option 2 to join game
echo.
pause
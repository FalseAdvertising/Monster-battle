@echo off
echo ========================================
echo Monster Battle - Network Multiplayer
echo ========================================
echo.

REM Quick dependency check
cd /d "%~dp0code"
python check_dependencies.py >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  Dependencies may be missing!
    echo.
    echo Choose an option:
    echo 0. Install/Setup Dependencies
    echo 1. Start Server (Host Game)
    echo 2. Start Client (Join Game) 
    echo 3. Check if Server is Running
    echo 4. Network Diagnostics (Find Servers)
    echo 5. Network Launcher (GUI)
    echo 6. Local Game (Single Computer)
    echo 7. Check Dependencies
    echo.
) else (
    echo ✅ Dependencies OK
    echo.
    echo Choose an option:
    echo 1. Start Server (Host Game)
    echo 2. Start Client (Join Game) 
    echo 3. Check if Server is Running
    echo 4. Network Diagnostics (Find Servers)
    echo 5. Network Launcher (GUI)
    echo 6. Local Game (Single Computer)
    echo 7. Check Dependencies
    echo 0. Install/Setup Dependencies
    echo.
)

set /p choice="Enter your choice: "

if "%choice%"=="0" (
    echo Running setup...
    cd /d "%~dp0"
    call setup.bat
    goto :eof
) else if "%choice%"=="1" (
    echo Starting server...
    echo Keep this window open while playing!
    python network_server.py
) else if "%choice%"=="2" (
    echo Starting client...
    python network_game.py
) else if "%choice%"=="3" (
    echo Checking server status...
    python check_server.py
) else if "%choice%"=="4" (
    echo Running network diagnostics...
    python network_diagnostics.py
) else if "%choice%"=="5" (
    echo Starting network launcher...
    python network_launcher.py
) else if "%choice%"=="6" (
    echo Starting local game...
    python main.py
) else if "%choice%"=="7" (
    echo Checking dependencies...
    python check_dependencies.py
) else (
    echo Invalid choice!
    pause
    goto :eof
)

pause
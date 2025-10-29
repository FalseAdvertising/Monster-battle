@echo off
echo ========================================
echo Monster Battle - Network Multiplayer
echo ========================================
echo.
echo Choose an option:
echo 1. Start Server (Host Game)
echo 2. Start Client (Join Game) 
echo 3. Check if Server is Running
echo 4. Network Diagnostics (Find Servers)
echo 5. Network Launcher (GUI)
echo 6. Local Game (Single Computer)
echo.
set /p choice="Enter your choice (1-6): "

cd /d "%~dp0code"

if "%choice%"=="1" (
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
) else (
    echo Invalid choice!
    pause
    goto :eof
)

pause
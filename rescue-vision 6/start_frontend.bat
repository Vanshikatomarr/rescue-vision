@echo off
title Rescue Vision - React Frontend Dashboard (Port 5173)
cd /d "%~dp0frontend"

echo ========================================================
echo       RESCUE VISION - REACT / VITE FRONTEND LAUNCHER
echo ========================================================
echo.

:: Check Node
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Node.js was not found in PATH!
    echo Please install Node.js 18+ from https://nodejs.org
    pause
    exit /b 1
)

:: Install dependencies if node_modules missing
if not exist "node_modules" (
    echo [INSTALL] node_modules not detected. Running npm install...
    call npm install
    if %errorlevel% neq 0 (
        echo [ERROR] npm install failed!
        pause
        exit /b 1
    )
)

echo.
echo ========================================================
echo [START] Starting Vite Dev Server on http://127.0.0.1:5173
echo Connecting to Backend API at http://127.0.0.1:8000
echo ========================================================
echo.

call npm run dev -- --host 127.0.0.1 --port 5173
if %errorlevel% neq 0 (
    echo [ERROR] Frontend server exited with code %errorlevel%.
    pause
)

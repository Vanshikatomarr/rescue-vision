@echo off
setlocal enabledelayedexpansion

echo ========================================================
echo       RESCUE VISION - ENVIRONMENT DIAGNOSTICS CHECK
echo ========================================================
echo.

set ERRORS=0

echo [1/4] Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not added to your system PATH.
    echo Please install Python 3.10+ from https://python.org
    set /a ERRORS+=1
) else (
    for /f "tokens=*" %%i in ('python --version') do echo [OK] %%i detected.
)
echo.

echo [2/4] Checking Node.js and npm...
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Node.js is not installed or not in PATH.
    echo Please install Node.js 18+ from https://nodejs.org
    set /a ERRORS+=1
) else (
    for /f "tokens=*" %%i in ('node --version') do echo [OK] Node.js %%i detected.
)

npm --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] npm is not installed or not in PATH.
    set /a ERRORS+=1
) else (
    for /f "tokens=*" %%i in ('npm --version') do echo [OK] npm %%i detected.
)
echo.

echo [3/4] Checking YOLO model weights...
if exist "backend\models\yolo26n.pt" (
    echo [OK] Base YOLO model weights found at backend\models\yolo26n.pt.
) else (
    if exist "models\yolo26n.pt" (
        echo [OK] Base YOLO model weights found at models\yolo26n.pt.
    ) else (
        echo [WARNING] yolo26n.pt not found in backend\models\. 
        echo Ultralytics will attempt to auto-download on first detection run.
    )
)
echo.

echo [4/4] Checking port availability (8000 and 5173)...
netstat -ano | findstr ":8000 " >nul 2>&1
if %errorlevel% equ 0 (
    echo [NOTICE] Port 8000 is currently in use. Ensure existing backend is closed before starting.
) else (
    echo [OK] Port 8000 is available.
)

netstat -ano | findstr ":5173 " >nul 2>&1
if %errorlevel% equ 0 (
    echo [NOTICE] Port 5173 is currently in use. Ensure existing frontend is closed before starting.
) else (
    echo [OK] Port 5173 is available.
)
echo.

echo ========================================================
if %ERRORS% equ 0 (
    echo [SUCCESS] All system prerequisites are satisfied!
) else (
    echo [FAILURE] Please resolve the %ERRORS% error(s) noted above.
)
echo ========================================================
echo.
pause

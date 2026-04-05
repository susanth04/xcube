@echo off
REM Launch script for X_Cube Gazebo Simulation System
REM Starts all required services in separate windows

echo ============================================================
echo X_Cube Gazebo Simulation System - Launcher
echo ============================================================
echo.

REM Configuration - Change this if your conda env has a different name
set CONDA_ENV=gazebo_harmonic

REM Check if conda is available
where conda >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Conda not found! Please install Miniconda or Anaconda.
    echo Visit: https://docs.conda.io/en/latest/miniconda.html
    pause
    exit /b 1
)

echo Using conda environment: %CONDA_ENV%
echo Starting services...
echo.

REM Start Gazebo Bridge (in conda environment)
echo [1/3] Starting Gazebo Bridge on port 8002...
start "Gazebo Bridge" cmd /k "call conda activate %CONDA_ENV% && cd /d %~dp0 && python gazebo_sim_bridge.py"
timeout /t 3 /nobreak >nul

REM Start Backend API (in conda environment)
echo [2/3] Starting Backend API on port 8000...
start "Backend API" cmd /k "call conda activate %CONDA_ENV% && cd /d %~dp0 && python -m uvicorn backend.api_server:app --host 0.0.0.0 --port 8000"
timeout /t 3 /nobreak >nul

REM Start Frontend
echo [3/3] Starting Frontend on port 3000...
start "Frontend" cmd /k "cd /d %~dp0simulation-ui && npm run dev"
timeout /t 5 /nobreak >nul

echo.
echo ============================================================
echo All services started!
echo ============================================================
echo.
echo Services:
echo   - Gazebo Bridge:  http://localhost:8002/health
echo   - Backend API:    http://localhost:8000/
echo   - Frontend:       http://localhost:3000/
echo.
echo Press any key to open frontend in browser...
pause >nul

start http://localhost:3000

echo.
echo Services are running in separate windows.
echo Close this window or press any key to exit launcher.
pause >nul

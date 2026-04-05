@echo off
REM Test script for X_Cube system
REM Tests all endpoints after services are started

echo ============================================================
echo X_Cube System Test Suite
echo ============================================================
echo.

REM Wait for services to be ready
echo Waiting for services to start...
timeout /t 5 /nobreak >nul

echo Running tests...
echo.

REM Test 1: Backend Health
echo [TEST 1/4] Backend Health Check
curl -s http://localhost:8000/ || echo FAILED
echo.

REM Test 2: Gazebo Bridge Health
echo [TEST 2/4] Gazebo Bridge Health Check
curl -s http://localhost:8002/health || echo FAILED
echo.

REM Test 3: Simple Chat Request
echo [TEST 3/4] Chat Request - Create Scene
curl -s -X POST http://localhost:8000/chat -H "Content-Type: application/json" -d "{\"prompt\":\"Create a warehouse\",\"session_id\":\"test\"}" || echo FAILED
echo.

REM Test 4: Complex Chat Request
echo [TEST 4/4] Chat Request - Complex Scene
curl -s -X POST http://localhost:8000/chat -H "Content-Type: application/json" -d "{\"prompt\":\"Create a warehouse with 2 robots and 3 boxes\",\"session_id\":\"test2\"}" || echo FAILED
echo.

echo ============================================================
echo Tests Complete!
echo ============================================================
pause

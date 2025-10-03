@echo off
echo ========================================
echo Clash Royale Deck Builder - Dev Start
echo ========================================
echo.

echo Starting Backend Server...
echo.
start "Backend Server" cmd /k "cd backend && uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000"

timeout /t 5 /nobreak > nul

echo Starting Frontend Server...
echo.
start "Frontend Server" cmd /k "cd frontend && npm start"

echo.
echo ========================================
echo Both servers are starting!
echo ========================================
echo.
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:3000
echo.
echo Press any key to close this window...
echo (The servers will keep running in their own windows)
pause > nul

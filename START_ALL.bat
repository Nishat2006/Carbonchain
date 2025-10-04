@echo off
echo ============================================
echo   STARTING EVERYTHING
echo ============================================
echo.

echo Starting Backend...
start "Backend" cmd /k "cd backend && python main.py"
timeout /t 2 /nobreak >nul

echo Starting Frontend...
start "Frontend" cmd /k "cd carbon-assessment && npm start"

echo.
echo ============================================
echo   SERVERS STARTING!
echo ============================================
echo.
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:3000
echo API Docs: http://localhost:8000/docs
echo.
echo Wait 30 seconds, then open: http://localhost:3000
echo.
pause

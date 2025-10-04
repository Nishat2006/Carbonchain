@echo off
echo ========================================
echo Blue Carbon Registry - Full Stack
echo ========================================
echo.
echo Starting Backend Server...
start "Backend Server" cmd /k "cd backend && python main.py"
timeout /t 3 /nobreak >nul
echo.
echo Starting Frontend Server...
start "Frontend Server" cmd /k "cd carbon-assessment && npm start"
echo.
echo ========================================
echo Servers Starting...
echo ========================================
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:3000
echo API Docs: http://localhost:8000/docs
echo ========================================
echo.
echo Press any key to stop both servers...
pause >nul
taskkill /FI "WindowTitle eq Backend Server*" /T /F
taskkill /FI "WindowTitle eq Frontend Server*" /T /F

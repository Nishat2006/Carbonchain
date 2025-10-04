@echo off
echo ========================================
echo Blue Carbon Registry Backend Server
echo ========================================
echo.
echo Installing dependencies...
pip install fastapi uvicorn sqlalchemy pydantic python-multipart aiofiles pillow httpx python-dateutil python-dotenv --quiet
echo.
echo Starting server...
echo Server will be available at: http://localhost:8000
echo API Documentation: http://localhost:8000/docs
echo.
python main.py
pause

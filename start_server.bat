@echo off
setlocal enabledelayedexpansion

REM Get the full path to Python
set PYTHON_PATH=C:\Users\Dens\AppData\Local\Programs\Python\Python314\python.exe

REM Check if Python exists
if not exist "%PYTHON_PATH%" (
    echo Error: Python not found at %PYTHON_PATH%
    pause
    exit /b 1
)

REM Change to project directory
cd /d "c:\Users\Dens\Desktop\Photoboothsystem\lookhere"

REM Install dependencies if needed
echo Checking dependencies...
"%PYTHON_PATH%" -m pip install -q Django==6.0.3 psycopg2-binary python-dotenv Pillow boto3

REM Start the server
echo.
echo ========================================
echo Photobooth Booking System
echo ========================================
echo.
echo Starting Django server...
echo.
echo Visit: http://localhost:8000
echo Admin: http://localhost:8000/admin
echo Login: admin / admin123
echo.
echo Press Ctrl+C to stop the server
echo.

"%PYTHON_PATH%" manage.py runserver 0.0.0.0:8000

pause
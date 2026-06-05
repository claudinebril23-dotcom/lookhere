@echo off
setlocal enabledelayedexpansion

echo Photobooth Booking System - Starting Server
echo ==========================================

REM Set Python path
set PYTHONPATH=C:\Users\Dens\AppData\Local\Programs\Python\Python314;%PYTHONPATH%

REM Change to project directory
cd /d "c:\Users\Dens\Desktop\Photoboothsystem\lookhere"

echo.
echo Python Version:
C:\Users\Dens\AppData\Local\Programs\Python\Python314\python.exe --version

echo.
echo Checking Django installation...
C:\Users\Dens\AppData\Local\Programs\Python\Python314\python.exe -c "import django; print(f'Django {django.VERSION} found')"

if %errorlevel% neq 0 (
    echo.
    echo Installing Django and dependencies...
    C:\Users\Dens\AppData\Local\Programs\Python\Python314\python.exe -m pip install -r requirements.txt
)

echo.
echo Starting Django development server...
echo.
echo PostgreSQL Database: photobooth_db
echo Admin Login: admin / admin123
echo.
echo Open your browser and go to:
echo   - Main site: http://localhost:8000
echo   - Admin panel: http://localhost:8000/admin
echo.
echo Press Ctrl+C to stop the server
echo.

C:\Users\Dens\AppData\Local\Programs\Python\Python314\python.exe manage.py runserver

pause
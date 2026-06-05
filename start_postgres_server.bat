@echo off
echo Starting Photobooth Booking System with PostgreSQL
echo ===================================================

cd /d "c:\Users\Dens\Desktop\Photoboothsystem\lookhere"

echo.
echo PostgreSQL Database: photobooth_db
echo Admin Login: admin / admin123
echo.
echo Starting Django development server...
echo.
echo Open your browser and go to:
echo   - Main site: http://localhost:8000
echo   - Admin panel: http://localhost:8000/admin
echo.

python manage.py runserver
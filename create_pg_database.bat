@echo off
echo Creating PostgreSQL database for Photobooth System...

set PGPATH="C:\Program Files\PostgreSQL\18\bin"
set PGPASSWORD=password

echo.
echo Connecting to PostgreSQL...
%PGPATH%\psql.exe -U postgres -h localhost -c "CREATE DATABASE photobooth_db;" 2>nul
if %errorlevel% equ 0 (
    echo Database 'photobooth_db' created successfully!
) else (
    echo Database 'photobooth_db' already exists or connection failed.
)

echo.
echo Checking database connection...
%PGPATH%\psql.exe -U postgres -h localhost -d photobooth_db -c "SELECT version();"

echo.
echo Database setup completed!
echo You can now run: python setup_database.py
pause
@echo off
echo PostgreSQL Password Reset Helper
echo ================================

echo.
echo Step 1: Stop PostgreSQL service
net stop postgresql-x64-18

echo.
echo Step 2: Starting PostgreSQL in single-user mode...
echo You'll need to run this command manually:
echo.
echo "C:\Program Files\PostgreSQL\18\bin\postgres.exe" --single -D "C:\Program Files\PostgreSQL\18\data" postgres

echo.
echo Step 3: In the single-user mode, run:
echo ALTER USER postgres PASSWORD 'newpassword';
echo.
echo Step 4: Exit and restart service:
echo net start postgresql-x64-18

pause
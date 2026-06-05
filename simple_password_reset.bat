@echo off
echo Testing PostgreSQL Password Reset
echo =================================

echo.
echo Please run this script as Administrator for full functionality.
echo.

echo Testing if we can connect with trust authentication...
"C:\Program Files\PostgreSQL\18\bin\psql.exe" -U postgres -h localhost -c "SELECT 'Connected!' as status;" 2>nul

if %errorlevel% equ 0 (
    echo Success! Setting password to 'password123'...
    "C:\Program Files\PostgreSQL\18\bin\psql.exe" -U postgres -h localhost -c "ALTER USER postgres PASSWORD 'password123';"
    
    echo Testing new password...
    set PGPASSWORD=password123
    "C:\Program Files\PostgreSQL\18\bin\psql.exe" -U postgres -h localhost -c "SELECT 'Password set successfully!' as result;"
    
    if %errorlevel% equ 0 (
        echo.
        echo SUCCESS! Your PostgreSQL password is now: password123
        echo.
    )
) else (
    echo Cannot connect. You may need to:
    echo 1. Run as Administrator
    echo 2. Modify pg_hba.conf manually
    echo 3. Or contact your system administrator
)

pause
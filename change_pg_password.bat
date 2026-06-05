@echo off
echo PostgreSQL Password Change Script
echo =================================

echo.
echo If you know your current PostgreSQL password, enter it when prompted.
echo If not, use pgAdmin method instead.
echo.

set /p CURRENT_PASSWORD=Enter current PostgreSQL password (or press Enter to skip): 

if "%CURRENT_PASSWORD%"=="" (
    echo Skipping command line method. Use pgAdmin instead.
    goto :end
)

echo.
echo Testing current password...
set PGPASSWORD=%CURRENT_PASSWORD%
"C:\Program Files\PostgreSQL\18\bin\psql.exe" -U postgres -h localhost -c "SELECT 'Current password works!' as status;"

if %errorlevel% equ 0 (
    echo.
    echo Current password verified! Changing to 'Claudine22'...
    "C:\Program Files\PostgreSQL\18\bin\psql.exe" -U postgres -h localhost -c "ALTER USER postgres PASSWORD 'Claudine22';"
    
    if %errorlevel% equ 0 (
        echo.
        echo SUCCESS! Password changed to: Claudine22
        echo.
        echo Testing new password...
        set PGPASSWORD=Claudine22
        "C:\Program Files\PostgreSQL\18\bin\psql.exe" -U postgres -h localhost -c "SELECT 'New password works!' as result;"
        
        if %errorlevel% equ 0 (
            echo.
            echo ========================================
            echo PASSWORD SUCCESSFULLY CHANGED!
            echo New password: Claudine22
            echo ========================================
        )
    ) else (
        echo Error: Could not change password
    )
) else (
    echo Current password is incorrect. Use pgAdmin method instead.
)

:end
echo.
echo To use pgAdmin:
echo 1. Open pgAdmin 4 from Start Menu
echo 2. Connect to PostgreSQL 18 server
echo 3. Right-click 'postgres' user → Properties → Definition
echo 4. Set password to: Claudine22
echo.
pause
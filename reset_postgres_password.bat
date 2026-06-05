@echo off
echo PostgreSQL Password Reset Process
echo ==================================

echo.
echo Step 1: Stopping PostgreSQL service...
net stop postgresql-x64-18

echo.
echo Step 2: Backing up pg_hba.conf...
copy "C:\Program Files\PostgreSQL\18\data\pg_hba.conf" "C:\Program Files\PostgreSQL\18\data\pg_hba.conf.backup"

echo.
echo Step 3: Modifying authentication to allow password reset...
echo # Temporary configuration for password reset > "C:\Program Files\PostgreSQL\18\data\pg_hba_temp.conf"
echo # TYPE  DATABASE        USER            ADDRESS                 METHOD >> "C:\Program Files\PostgreSQL\18\data\pg_hba_temp.conf"
echo local   all             postgres                                trust >> "C:\Program Files\PostgreSQL\18\data\pg_hba_temp.conf"
echo host    all             postgres        127.0.0.1/32            trust >> "C:\Program Files\PostgreSQL\18\data\pg_hba_temp.conf"
echo host    all             postgres        ::1/128                 trust >> "C:\Program Files\PostgreSQL\18\data\pg_hba_temp.conf"
echo host    all             all             127.0.0.1/32            md5 >> "C:\Program Files\PostgreSQL\18\data\pg_hba_temp.conf"
echo host    all             all             ::1/128                 md5 >> "C:\Program Files\PostgreSQL\18\data\pg_hba_temp.conf"

copy "C:\Program Files\PostgreSQL\18\data\pg_hba_temp.conf" "C:\Program Files\PostgreSQL\18\data\pg_hba.conf"

echo.
echo Step 4: Starting PostgreSQL service...
net start postgresql-x64-18

echo.
echo Step 5: Waiting for service to start...
timeout /t 5

echo.
echo Step 6: Resetting password to 'password123'...
"C:\Program Files\PostgreSQL\18\bin\psql.exe" -U postgres -h localhost -c "ALTER USER postgres PASSWORD 'password123';"

if %errorlevel% equ 0 (
    echo SUCCESS! Password has been reset to: password123
    
    echo.
    echo Step 7: Restoring original authentication settings...
    copy "C:\Program Files\PostgreSQL\18\data\pg_hba.conf.backup" "C:\Program Files\PostgreSQL\18\data\pg_hba.conf"
    
    echo.
    echo Step 8: Restarting PostgreSQL service...
    net stop postgresql-x64-18
    net start postgresql-x64-18
    
    echo.
    echo Step 9: Testing new password...
    timeout /t 3
    set PGPASSWORD=password123
    "C:\Program Files\PostgreSQL\18\bin\psql.exe" -U postgres -h localhost -c "SELECT 'Password reset successful!' as result;"
    
    if %errorlevel% equ 0 (
        echo.
        echo ========================================
        echo SUCCESS! PostgreSQL password is now: password123
        echo Update your .env file with this password
        echo ========================================
    ) else (
        echo Error: Password reset may have failed
    )
) else (
    echo Error: Could not reset password
    echo Restoring backup...
    copy "C:\Program Files\PostgreSQL\18\data\pg_hba.conf.backup" "C:\Program Files\PostgreSQL\18\data\pg_hba.conf"
    net stop postgresql-x64-18
    net start postgresql-x64-18
)

echo.
echo Cleaning up temporary files...
del "C:\Program Files\PostgreSQL\18\data\pg_hba_temp.conf" 2>nul

pause
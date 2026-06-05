@echo off
echo Testing PostgreSQL Passwords...
echo ================================

set PGPATH="C:\Program Files\PostgreSQL\18\bin"

echo Testing common passwords...

echo.
echo Testing password: postgres
set PGPASSWORD=postgres
%PGPATH%\psql.exe -U postgres -h localhost -c "SELECT 'SUCCESS: postgres' as result;" 2>nul
if %errorlevel% equ 0 (
    echo SUCCESS! Password is: postgres
    goto :found
)

echo.
echo Testing password: admin
set PGPASSWORD=admin
%PGPATH%\psql.exe -U postgres -h localhost -c "SELECT 'SUCCESS: admin' as result;" 2>nul
if %errorlevel% equ 0 (
    echo SUCCESS! Password is: admin
    goto :found
)

echo.
echo Testing password: password
set PGPASSWORD=password
%PGPATH%\psql.exe -U postgres -h localhost -c "SELECT 'SUCCESS: password' as result;" 2>nul
if %errorlevel% equ 0 (
    echo SUCCESS! Password is: password
    goto :found
)

echo.
echo Testing password: 123456
set PGPASSWORD=123456
%PGPATH%\psql.exe -U postgres -h localhost -c "SELECT 'SUCCESS: 123456' as result;" 2>nul
if %errorlevel% equ 0 (
    echo SUCCESS! Password is: 123456
    goto :found
)

echo.
echo Testing empty password
set PGPASSWORD=
%PGPATH%\psql.exe -U postgres -h localhost -c "SELECT 'SUCCESS: empty' as result;" 2>nul
if %errorlevel% equ 0 (
    echo SUCCESS! Password is empty
    goto :found
)

echo.
echo None of the common passwords worked.
echo You may need to reset the PostgreSQL password.
echo.
echo To reset password:
echo 1. Stop PostgreSQL service: net stop postgresql-x64-18
echo 2. Edit pg_hba.conf to use 'trust' authentication
echo 3. Restart service: net start postgresql-x64-18
echo 4. Connect and change password: ALTER USER postgres PASSWORD 'newpassword';
goto :end

:found
echo.
echo Found working password! Update your .env file with this password.
echo.

:end
pause
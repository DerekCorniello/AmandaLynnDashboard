echo Checking if Docker is running...
@echo off
docker info >nul 2>&1

if %errorlevel% neq 0 (
    echo Docker is not running. Starting Docker...
    start "" "C:\Program Files\Docker\Docker\Docker Desktop.exe"
    timeout /t 30 /nobreak
)

echo Starting Docker Compose services without rebuilding...

docker-compose up -d

echo Waiting for Django server...

set "django_url=http://localhost:8000/api/status/"
set "app_url=http://localhost:8081"
set "timeout=5"

:check_django
powershell -Command "(Invoke-WebRequest -Uri '%django_url%' -UseBasicParsing).StatusCode" >nul 2>&1
if errorlevel 1 (
    echo Waiting for Django server to respond...
    timeout /t %timeout% >nul
    goto :check_django
)

echo Django server is up. Starting up your app...

:check_app
powershell -Command "(Invoke-WebRequest -Uri '%app_url%' -UseBasicParsing).StatusCode" >nul 2>&1
if errorlevel 1 (
    echo Waiting for the app to respond...
    timeout /t %timeout% >nul
    goto :check_app
)

start "" %app_url%
echo App Started, press any key to close the app.
echo You can minimize, but do not close, the window.

pause >nul

docker-compose down

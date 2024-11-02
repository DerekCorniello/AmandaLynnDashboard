@echo off
echo Checking if Docker is running...
docker info >nul 2>&1

if %errorlevel% neq 0 (
    echo Docker is not running. Starting Docker...
    start "" "C:\Program Files\Docker\Docker\Docker Desktop.exe"
    timeout /t 30 /nobreak
)

echo Pulling latest code from Git...
git pull origin main

echo Stopping any running Docker services...
docker-compose down

echo Removing old builds...
docker image prune -f
docker volume prune -f

echo Updating application, this may take a while...
docker-compose build --no-cache

docker-compose up -d

echo Update complete. Starting app...

REM Wait here for both the Django server and the app to respond

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

echo Django server is up. Checking app...

:check_app
powershell -Command "(Invoke-WebRequest -Uri '%app_url%' -UseBasicParsing).StatusCode" >nul 2>&1
if errorlevel 1 (
    echo Waiting for the app to respond...
    timeout /t %timeout% >nul
    goto :check_app
)

start "" %app_url%
echo App updated and started! Press any key to close the app.
pause >nul

docker-compose down

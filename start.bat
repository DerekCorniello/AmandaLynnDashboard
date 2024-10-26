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

echo Starting up your app...

timeout /t 30 /nobreak >nul
start "" http://localhost:8081

echo App Started, press any key to close the app.
echo You can minimize, but do not close, the window.

pause >nul

docker-compose down

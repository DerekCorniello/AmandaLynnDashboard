@echo off
echo Checking if Docker is running...
docker info >nul 2>&1

if %errorlevel% neq 0 (
    echo Docker is not running. Starting Docker...
    start "" "C:\Program Files\Docker\Docker\Docker Desktop.exe"
    timeout /t 30 /nobreak
)

echo Starting Docker Compose services...
docker-compose up --build --remove-orphans
pause

echo Checking if Docker is running...
@echo off
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

echo Building Docker Compose services...
docker-compose up --build -d

echo Updating... this may take a while

timeout /t 60 /nobreak >nul

start "" http://localhost:8081

echo App updated and started! Press any key to close the app.
pause >nul

docker-compose down

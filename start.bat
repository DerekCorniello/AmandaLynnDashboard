echo Checking if Docker is running...
@echo off
docker info >nul 2>&1

if %errorlevel% neq 0 (
    echo Docker is not running. Starting Docker...
    start "" "C:\Program Files\Docker\Docker\Docker Desktop.exe"
    timeout /t 30 /nobreak
)

echo Starting Docker Compose services...

docker volume create sql-data

docker build -t frontend-image ./frontend
docker build -t backend-image .

docker run -d --name frontend-container -p 8081:8080 frontend-image
docker run -d --name backend-container -v sql-data:/app -p 8000:8000 backend-image

echo Build Complete. Your app window will open soon.

timeout /t 5 /nobreak >nul

start "" http://localhost:8081

echo App Started, press any key to close the app.
echo You can minimize, but do not close, the window.

pause >nul

docker stop frontend-container backend-container
docker rm frontend-container backend-container

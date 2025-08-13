@echo off
REM Boardy - IBM Onboarding Assistant
REM Start/Restart Script

echo.
echo ================================
echo   Boardy Onboarding Assistant   
echo ================================
echo.

REM Check if .env file exists
if not exist ".env" (
    echo [ERROR] .env file not found!
    echo.
    echo Please create a .env file with your Watson X credentials:
    echo   WATSONX_API_KEY=your_api_key
    echo   WATSONX_PROJECT_ID=your_project_id
    echo   WATSONX_URL=https://us-south.ml.cloud.ibm.com
    echo.
    pause
    exit /b 1
)

echo [INFO] Stopping any running containers...
wsl --distribution Ubuntu --exec bash -c "cd /mnt/c/Users/SofiePischl/Documents/01_HdM/watsonx-chat-starter && podman-compose down" 2>nul

echo [INFO] Starting Boardy application...
echo.

wsl --distribution Ubuntu --exec bash -c "cd /mnt/c/Users/SofiePischl/Documents/01_HdM/watsonx-chat-starter && podman-compose up --build -d"

if %errorlevel% equ 0 (
    echo.
    echo ================================
    echo   SUCCESS: Boardy is running!   
    echo ================================
    echo.
    echo Access the application:
    echo   Frontend: http://localhost:8000
    echo   API:      http://localhost:8000/api/chat
    echo.
    echo Press any key to open in browser...
    pause >nul
    start http://localhost:8000
) else (
    echo.
    echo [ERROR] Failed to start application!
    echo Check the error messages above.
    pause
)
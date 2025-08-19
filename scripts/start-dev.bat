@echo off
REM Boardy - IBM Onboarding Assistant
REM Development Startup Script

echo.
echo ========================================
echo   Boardy Onboarding Assistant - DEV   
echo ========================================
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
pushd %~dp0..
set "WSL_PATH=%cd:C:=/mnt/c%"
set "WSL_PATH=%WSL_PATH:\=/%"
wsl --distribution Ubuntu --exec bash -c "cd '%WSL_PATH%' && podman-compose down" 2>nul
popd

echo [INFO] Starting Backend services...
echo.

REM Start backend services
pushd %~dp0..
set "WSL_PATH=%cd:C:=/mnt/c%"
set "WSL_PATH=%WSL_PATH:\=/%"
wsl --distribution Ubuntu --exec bash -c "cd '%WSL_PATH%' && podman-compose up --build -d"
set "BACKEND_EXIT_CODE=%errorlevel%"
popd

if %BACKEND_EXIT_CODE% equ 0 (
    echo.
    echo ========================================
    echo   SUCCESS: Backend is running!   
    echo ========================================
    echo.
    echo Starting Frontend development server...
    echo.
    
    REM Start frontend development server in background
    cd /d %~dp0..\frontend
    start /b npm run dev
    
    REM Wait a moment for the server to start
    timeout /t 3 /nobreak >nul
    
    echo.
    echo ========================================
    echo   SUCCESS: All services running!   
    echo ========================================
    echo.
    echo Access the application:
    echo   Frontend: http://localhost:5173 (Vite dev server - HOT RELOAD!)
    echo   Backend:  http://localhost:8000
    echo   API:      http://localhost:8000/api/chat
    echo.
    echo The frontend will automatically reload when you make changes!
    echo.


@echo off
echo ========================================
echo  Boardy Frontend Setup Script
echo ========================================
echo.

echo [1/4] Checking Node.js installation...
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Node.js is not installed!
    echo Please install Node.js from https://nodejs.org/
    pause
    exit /b 1
)
echo ✓ Node.js is installed

echo.
echo [2/4] Navigating to frontend directory...
cd /d "%~dp0frontend"
if not exist "package.json" (
    echo ERROR: package.json not found in frontend directory!
    echo Please make sure you're in the correct project directory.
    pause
    exit /b 1
)
echo ✓ Frontend directory found

echo.
echo [3/4] Installing dependencies...
call npm install
if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies!
    pause
    exit /b 1
)
echo ✓ Dependencies installed successfully

echo.
echo [4/4] Building frontend...
call npm run build
if %errorlevel% neq 0 (
    echo ERROR: Build failed!
    pause
    exit /b 1
)
echo ✓ Frontend built successfully

echo.
echo ========================================
echo  Setup completed successfully!
echo ========================================
echo.
echo Next steps:
echo 1. Start development server: npm run dev
echo 2. Open browser: http://localhost:5173
echo 3. Backend is already deployed and connected
echo.
echo Press any key to start the development server...
pause >nul

echo.
echo Starting development server...
call npm run dev

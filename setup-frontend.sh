#!/bin/bash

echo "========================================"
echo " Boardy Frontend Setup Script"
echo "========================================"
echo

echo "[1/4] Checking Node.js installation..."
if ! command -v node &> /dev/null; then
    echo "ERROR: Node.js is not installed!"
    echo "Please install Node.js from https://nodejs.org/"
    exit 1
fi
echo "✓ Node.js is installed ($(node --version))"

echo
echo "[2/4] Navigating to frontend directory..."
cd "$(dirname "$0")/frontend"
if [ ! -f "package.json" ]; then
    echo "ERROR: package.json not found in frontend directory!"
    echo "Please make sure you're in the correct project directory."
    exit 1
fi
echo "✓ Frontend directory found"

echo
echo "[3/4] Installing dependencies..."
npm install
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install dependencies!"
    exit 1
fi
echo "✓ Dependencies installed successfully"

echo
echo "[4/4] Building frontend..."
npm run build
if [ $? -ne 0 ]; then
    echo "ERROR: Build failed!"
    exit 1
fi
echo "✓ Frontend built successfully"

echo
echo "========================================"
echo " Setup completed successfully!"
echo "========================================"
echo
echo "Next steps:"
echo "1. Start development server: npm run dev"
echo "2. Open browser: http://localhost:5173"
echo "3. Backend is already deployed and connected"
echo
echo "Press Enter to start the development server..."
read

echo
echo "Starting development server..."
npm run dev

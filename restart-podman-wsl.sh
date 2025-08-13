#!/bin/bash

# Watson X Chat Starter - Podman WSL Restart Script
echo "Restarting Watson X Chat Application..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in WSL
if [[ ! -f /proc/version ]] || ! grep -q Microsoft /proc/version; then
    print_error "This script must be run in WSL (Windows Subsystem for Linux)"
    exit 1
fi

# Check if podman-compose is installed
if ! command -v podman-compose &> /dev/null; then
    print_error "podman-compose is not installed!"
    print_status "Please install it first: pip install podman-compose"
    exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    print_error ".env file not found!"
    print_status "Please create a .env file with your Watson X credentials first."
    exit 1
fi

print_status "Checking current container status..."
podman-compose -f podman-compose.yml ps

echo ""
print_status "Stopping all containers..."
if podman-compose -f podman-compose.yml down; then
    print_success "All containers stopped successfully!"
else
    print_warning "Some containers might not have been running or failed to stop."
fi

# Wait a moment for cleanup
sleep 3

echo ""
print_status "Starting containers with fresh build..."
if podman-compose -f podman-compose.yml up --build -d; then
    print_success "Containers started successfully!"
else
    print_error "Failed to start containers!"
    exit 1
fi

# Wait for services to start
print_status "Waiting for services to start up..."
sleep 10

# Check if services are running
print_status "Checking service status..."
if podman-compose -f podman-compose.yml ps | grep -q "Up"; then
    print_success "All services are running!"
    
    # Test if backend is responding
    print_status "Testing backend connectivity..."
    if curl -s http://localhost:8000/healthz > /dev/null; then
        print_success "Backend is responding!"
    else
        print_warning "Backend might still be starting up..."
        print_status "Waiting a bit longer..."
        sleep 5
        
        if curl -s http://localhost:8000/healthz > /dev/null; then
            print_success "Backend is now responding!"
        else
            print_warning "Backend might need more time to start..."
        fi
    fi
    
    echo ""
    print_success "Application restarted successfully!"
    echo "=================================================="
    echo "Frontend: http://localhost:8000"
    echo "LiteLLM API: http://localhost:4000"
    echo "Health Check: http://localhost:8000/healthz"
    echo "=================================================="
    echo ""
    print_status "Container status:"
    podman-compose -f podman-compose.yml ps
    
    echo ""
    print_status "Useful commands:"
    print_status "  - View logs: podman-compose -f podman-compose.yml logs -f"
    print_status "  - Stop app: ./stop-podman-wsl.sh"
    print_status "  - Restart app: ./restart-podman-wsl.sh"
    
else
    print_error "Some services failed to start!"
    print_status "Container status:"
    podman-compose -f podman-compose.yml ps
    print_status "Recent logs:"
    podman-compose -f podman-compose.yml logs --tail=20
    exit 1
fi 
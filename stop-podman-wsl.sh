#!/bin/bash

# Watson X Chat Starter - Podman WSL Stop Script
echo "Stopping Watson X Chat Application..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
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
    exit 1
fi

# Check if containers are running
if ! podman-compose -f podman-compose.yml ps | grep -q "Up"; then
    print_status "No containers are currently running."
    exit 0
fi

print_status "Current container status:"
podman-compose -f podman-compose.yml ps

print_status "Stopping containers..."
if podman-compose -f podman-compose.yml down; then
    print_success "Containers stopped successfully!"
else
    print_error "Failed to stop some containers!"
    exit 1
fi

print_status "Container status after stopping:"
podman-compose -f podman-compose.yml ps

print_success "Application stopped successfully!"
print_status "To start again, run: ./start-podman-wsl.sh" 
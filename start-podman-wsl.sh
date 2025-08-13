
#!/bin/bash

# Watson X Chat Starter - Podman WSL Startup Script
echo "Starting Watson X Chat Application with Podman in WSL..."

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

# Check if .env file exists
if [ ! -f .env ]; then
    print_warning ".env file not found!"
    print_status "Creating example .env file..."
    
    cat > .env << EOF
# Watson X API Configuration
# Replace these values with your actual Watson X credentials

WATSONX_API_KEY=your_api_key_here
WATSONX_PROJECT_ID=your_project_id_here
WATSONX_URL=https://us-south.ml.cloud.ibm.com

# Optional: Model configuration
MODEL_NAME=llama-3-8b

# Optional: Backend configuration
HOST=0.0.0.0
PORT=8000
RELOAD=false
EOF
    
    print_warning "Example .env file created. Please edit it with your Watson X credentials."
    print_status "Then restart the application."
    exit 1
fi

# Check if podman is installed
if ! command -v podman &> /dev/null; then
    print_error "Podman is not installed!"
    print_status "Please install Podman first: sudo apt update && sudo apt install -y podman"
    exit 1
fi

# Check if podman-compose is installed
if ! command -v podman-compose &> /dev/null; then
    print_error "podman-compose is not installed!"
    print_status "Please install podman-compose: pip install podman-compose"
    exit 1
fi

print_success "Podman and podman-compose found"

# Check if containers are already running
if podman-compose -f podman-compose.yml ps | grep -q "Up"; then
    print_warning "Containers are already running!"
    print_status "Current container status:"
    podman-compose -f podman-compose.yml ps
    
    read -p "Do you want to restart the containers? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_status "Stopping existing containers..."
        podman-compose -f podman-compose.yml down
        sleep 2
    else
        print_status "Using existing containers."
        print_success "Application is already running!"
        print_status "Frontend: http://localhost:8000"
        print_status "LiteLLM API: http://localhost:4000"
        exit 0
    fi
fi

# Build and start the containers
print_status "Building and starting containers..."
if podman-compose -f podman-compose.yml up --build -d; then
    print_success "Containers started successfully!"
else
    print_error "Failed to start containers!"
    exit 1
fi

# Wait for services to start
print_status "Waiting for services to start..."
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
    fi
    
    echo
    print_success "Application started successfully!"
    echo "=================================================="
    echo "Frontend: http://localhost:8000"
    echo "LiteLLM API: http://localhost:4000"
    echo "Health Check: http://localhost:8000/healthz"
    echo "=================================================="
    echo
    print_status "To stop the application, run: ./stop-podman-wsl.sh"
    print_status "To view logs, run: podman-compose -f podman-compose.yml logs -f"
    print_status "To check status, run: podman-compose -f podman-compose.yml ps"
    
else
    print_error "Some services failed to start!"
    print_status "Container status:"
    podman-compose -f podman-compose.yml ps
    print_status "Logs:"
    podman-compose -f podman-compose.yml logs
    exit 1
fi 
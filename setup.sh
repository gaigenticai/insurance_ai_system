#!/bin/bash

# Insurance AI System - One-Click Setup Script
# This script sets up the complete Insurance AI System with Docker

set -e  # Exit on any error

echo "🚀 Insurance AI System - One-Click Setup"
echo "========================================"

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

# Check if Docker is installed
check_docker() {
    print_status "Checking Docker installation..."
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        echo "Visit: https://docs.docker.com/get-docker/"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        echo "Visit: https://docs.docker.com/compose/install/"
        exit 1
    fi
    
    print_success "Docker and Docker Compose are installed"
}

# Check if Docker daemon is running
check_docker_daemon() {
    print_status "Checking Docker daemon..."
    if ! docker info &> /dev/null; then
        print_error "Docker daemon is not running. Please start Docker first."
        exit 1
    fi
    print_success "Docker daemon is running"
}

# Setup environment file
setup_env() {
    print_status "Setting up environment configuration..."
    
    if [ ! -f .env ]; then
        cp .env.example .env
        print_success "Created .env file from template"
        print_warning "Please edit .env file and add your API keys:"
        print_warning "  - OPENAI_API_KEY=your_openai_api_key"
        print_warning "  - ANTHROPIC_API_KEY=your_anthropic_api_key"
        echo ""
        read -p "Press Enter to continue after editing .env file..."
    else
        print_success ".env file already exists"
    fi
}

# Build Docker images
build_images() {
    print_status "Building Docker images..."
    docker-compose build --no-cache
    print_success "Docker images built successfully"
}

# Start services
start_services() {
    print_status "Starting services..."
    docker-compose up -d postgres redis
    print_status "Waiting for database to be ready..."
    sleep 10
    
    print_status "Running database migrations..."
    docker-compose run --rm api python db_migrations.py
    
    print_status "Starting all services..."
    docker-compose up -d
    print_success "All services started successfully"
}

# Check service health
check_services() {
    print_status "Checking service health..."
    
    # Wait for services to start
    sleep 15
    
    # Check API health
    if curl -f http://localhost:8080/health &> /dev/null; then
        print_success "API service is healthy"
    else
        print_warning "API service may not be ready yet"
    fi
    
    # Check UI
    if curl -f http://localhost:8501 &> /dev/null; then
        print_success "UI service is healthy"
    else
        print_warning "UI service may not be ready yet"
    fi
}

# Display service URLs
show_urls() {
    echo ""
    echo "🎉 Setup Complete!"
    echo "=================="
    echo ""
    echo "📊 Service URLs:"
    echo "  • API Server:     http://localhost:8080"
    echo "  • API Docs:       http://localhost:8080/docs"
    echo "  • Streamlit UI:   http://localhost:8501"
    echo "  • PostgreSQL:     localhost:5432"
    echo "  • Redis:          localhost:6379"
    echo ""
    echo "🤖 AI Features:"
    echo "  • Underwriting:   POST /ai/underwriting/analyze"
    echo "  • Claims:         POST /ai/claims/analyze"
    echo "  • Actuarial:      POST /ai/actuarial/analyze"
    echo "  • Configuration:  GET/POST /ai/configuration"
    echo "  • Health Check:   GET /ai/health"
    echo ""
    echo "📚 Documentation:"
    echo "  • AI Features:    docs/AI_FEATURES.md"
    echo "  • Implementation: AI_IMPLEMENTATION_SUMMARY.md"
    echo ""
    echo "🔧 Management Commands:"
    echo "  • View logs:      docker-compose logs -f"
    echo "  • Stop services:  docker-compose down"
    echo "  • Restart:        docker-compose restart"
    echo "  • Update:         docker-compose pull && docker-compose up -d"
    echo ""
}

# Test AI functionality
test_ai() {
    print_status "Testing AI functionality..."
    
    if python test_ai_simple.py &> /dev/null; then
        print_success "AI components test passed"
    else
        print_warning "AI components test failed - check your API keys"
    fi
}

# Main setup flow
main() {
    echo "This script will:"
    echo "  1. Check Docker installation"
    echo "  2. Setup environment configuration"
    echo "  3. Build Docker images"
    echo "  4. Start all services"
    echo "  5. Run database migrations"
    echo "  6. Test AI functionality"
    echo ""
    
    read -p "Continue? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Setup cancelled."
        exit 0
    fi
    
    check_docker
    check_docker_daemon
    setup_env
    build_images
    start_services
    check_services
    test_ai
    show_urls
    
    print_success "Insurance AI System is now running!"
}

# Handle script arguments
case "${1:-}" in
    "start")
        print_status "Starting services..."
        docker-compose up -d
        print_success "Services started"
        ;;
    "stop")
        print_status "Stopping services..."
        docker-compose down
        print_success "Services stopped"
        ;;
    "restart")
        print_status "Restarting services..."
        docker-compose restart
        print_success "Services restarted"
        ;;
    "logs")
        docker-compose logs -f
        ;;
    "test")
        test_ai
        ;;
    "clean")
        print_status "Cleaning up..."
        docker-compose down -v
        docker system prune -f
        print_success "Cleanup complete"
        ;;
    *)
        main
        ;;
esac
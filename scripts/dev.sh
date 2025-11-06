#!/bin/bash
# Wara9a development task runner for Unix/Linux/macOS
# Usage: ./scripts/dev.sh [command]

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper function for colored output
log_info() {
    echo -e "${BLUE}🔄 $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Show help
show_help() {
    echo "Wara9a Development Commands:"
    echo ""
    echo "Setup:"
    echo "  install      Install basic dependencies"
    echo "  install-dev  Install development dependencies"
    echo "  install-full Install all dependencies"
    echo ""
    echo "Development:"
    echo "  test         Run tests"
    echo "  format       Format code (black + isort)"
    echo "  lint         Run linting (flake8 + mypy)"
    echo "  clean        Clean build artifacts"
    echo ""
    echo "Demo:"
    echo "  demo         Run demo script"
    echo "  check        Run all quality checks"
}

# Installation functions
install_basic() {
    log_info "Installing basic dependencies..."
    pip install -r requirements.txt
    log_success "Basic dependencies installed"
}

install_dev() {
    log_info "Installing development dependencies..."
    pip install -r requirements-dev.txt
    pip install -e .
    log_success "Development environment ready"
}

install_full() {
    log_info "Installing all dependencies..."
    pip install -r requirements-full.txt
    pip install -e .
    log_success "Full installation complete"
}

# Development functions
run_tests() {
    log_info "Running tests..."
    python -m pytest
    log_success "Tests completed"
}

format_code() {
    log_info "Formatting code..."
    python -m black wara9a tests demo.py scripts/
    python -m isort wara9a tests demo.py scripts/
    log_success "Code formatting complete"
}

lint_code() {
    log_info "Running linting..."
    python -m flake8 wara9a tests
    python -m mypy wara9a
    log_success "Linting complete"
}

clean_project() {
    log_info "Cleaning build artifacts..."
    python scripts/dev.py clean
    log_success "Project cleaned"
}

run_demo() {
    log_info "Running demo..."
    python demo.py
    log_success "Demo completed"
}

run_check() {
    log_info "Running all quality checks..."
    python scripts/dev.py check
}

# Main logic
case "${1:-help}" in
    help)
        show_help
        ;;
    install)
        install_basic
        ;;
    install-dev)
        install_dev
        ;;
    install-full)
        install_full
        ;;
    test)
        run_tests
        ;;
    format)
        format_code
        ;;
    lint)
        lint_code
        ;;
    clean)
        clean_project
        ;;
    demo)
        run_demo
        ;;
    check)
        run_check
        ;;
    *)
        log_error "Unknown command: $1"
        echo ""
        show_help
        exit 1
        ;;
esac
#!/usr/bin/env python3
"""
Setup script for Wara9a development environment
"""

import subprocess
import sys
from pathlib import Path


def run_command(command: str, description: str) -> bool:
    """Run a shell command and return success status"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False


def main():
    """Setup development environment"""
    print("🚀 Setting up Wara9a development environment")
    
    # Check if we're in a virtual environment
    if sys.prefix == sys.base_prefix:
        print("⚠️  Warning: You're not in a virtual environment")
        response = input("Continue anyway? (y/N): ").lower().strip()
        if response != 'y':
            print("Please create and activate a virtual environment first:")
            print("  python -m venv venv")
            print("  source venv/bin/activate  # On Windows: venv\\Scripts\\activate")
            sys.exit(1)
    
    # Install requirements
    success = True
    success &= run_command("pip install --upgrade pip", "Upgrading pip")
    success &= run_command("pip install -r requirements-dev.txt", "Installing development dependencies")
    success &= run_command("pip install -e .", "Installing Wara9a in development mode")
    
    # Setup pre-commit hooks
    success &= run_command("pre-commit install", "Setting up pre-commit hooks")
    
    # Run initial tests
    if success:
        print("\n🧪 Running initial tests...")
        success &= run_command("pytest --version", "Checking pytest")
        success &= run_command("wara9a --version", "Checking Wara9a installation")
    
    if success:
        print("\n🎉 Development environment setup completed!")
        print("\nNext steps:")
        print("  1. Run tests: pytest")
        print("  2. Try the demo: python demo.py")
        print("  3. Start developing: wara9a --help")
    else:
        print("\n❌ Setup failed. Please check the errors above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
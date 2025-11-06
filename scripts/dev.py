#!/usr/bin/env python3
"""
Wara9a development task runner
Cross-platform alternative to Makefile
"""

import argparse
import subprocess
import sys
from pathlib import Path


def run_command(command: str, description: str = None) -> bool:
    """Run a shell command and return success status"""
    if description:
        print(f"🔄 {description}...")
    
    try:
        result = subprocess.run(command, shell=True, check=True)
        if description:
            print(f"✅ {description} completed")
        return True
    except subprocess.CalledProcessError as e:
        if description:
            print(f"❌ {description} failed with exit code {e.returncode}")
        return False


def install_basic():
    """Install basic dependencies"""
    return run_command("pip install -r requirements.txt", "Installing basic dependencies")


def install_dev():
    """Install development dependencies"""
    success = run_command("pip install -r requirements-dev.txt", "Installing development dependencies")
    success &= run_command("pip install -e .", "Installing Wara9a in editable mode")
    return success


def install_full():
    """Install all dependencies"""
    return run_command("pip install -r requirements-full.txt", "Installing all dependencies")


def run_tests():
    """Run tests"""
    return run_command("python -m pytest", "Running tests")


def run_tests_with_coverage():
    """Run tests with coverage"""
    return run_command("python -m pytest --cov=wara9a --cov-report=html --cov-report=term", 
                      "Running tests with coverage")


def format_code():
    """Format code with black and isort"""
    success = run_command("python -m black wara9a tests demo.py scripts/", "Formatting with black")
    success &= run_command("python -m isort wara9a tests demo.py scripts/", "Sorting imports")
    return success


def lint_code():
    """Run linting"""
    success = run_command("python -m flake8 wara9a tests", "Running flake8")
    success &= run_command("python -m mypy wara9a", "Running mypy")
    return success


def clean_project():
    """Clean build artifacts"""
    import shutil
    
    patterns_to_remove = [
        "**/__pycache__",
        "**/*.pyc",
        "**/*.pyo", 
        "**/*.egg-info",
        "build/",
        "dist/",
        ".coverage",
        "htmlcov/",
        ".pytest_cache/",
        "demo_output/",
        "temp_project/",
        "output/",
        "generated_docs/"
    ]
    
    for pattern in patterns_to_remove:
        for path in Path(".").glob(pattern):
            if path.exists():
                if path.is_dir():
                    shutil.rmtree(path)
                    print(f"🗑️  Removed directory: {path}")
                else:
                    path.unlink()
                    print(f"🗑️  Removed file: {path}")


def run_demo():
    """Run demo script"""
    return run_command("python demo.py", "Running demo")


def main():
    parser = argparse.ArgumentParser(description="Wara9a development task runner")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Installation commands
    subparsers.add_parser("install", help="Install basic dependencies")
    subparsers.add_parser("install-dev", help="Install development dependencies")
    subparsers.add_parser("install-full", help="Install all dependencies")
    
    # Development commands
    subparsers.add_parser("test", help="Run tests")
    subparsers.add_parser("test-cov", help="Run tests with coverage")
    subparsers.add_parser("format", help="Format code (black + isort)")
    subparsers.add_parser("lint", help="Run linting (flake8 + mypy)")
    subparsers.add_parser("clean", help="Clean build artifacts")
    
    # Demo commands
    subparsers.add_parser("demo", help="Run demo script")
    
    # Quality check
    subparsers.add_parser("check", help="Run all quality checks (format + lint + test)")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    success = True
    
    if args.command == "install":
        success = install_basic()
    elif args.command == "install-dev":
        success = install_dev()
    elif args.command == "install-full":
        success = install_full()
    elif args.command == "test":
        success = run_tests()
    elif args.command == "test-cov":
        success = run_tests_with_coverage()
    elif args.command == "format":
        success = format_code()
    elif args.command == "lint":
        success = lint_code()
    elif args.command == "clean":
        clean_project()
    elif args.command == "demo":
        success = run_demo()
    elif args.command == "check":
        print("🔍 Running all quality checks...")
        success = format_code()
        success &= lint_code() 
        success &= run_tests()
        if success:
            print("🎉 All checks passed!")
        else:
            print("❌ Some checks failed!")
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
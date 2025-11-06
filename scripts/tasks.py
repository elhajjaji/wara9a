# Wara9a - Modern Python Project Task Runner
# Usage: python -m scripts.tasks [command]

"""
Modern task runner using Python and pyproject.toml
This is the most Pythonic and cross-platform approach
"""

import subprocess
import sys
from pathlib import Path


class TaskRunner:
    """Simple task runner for development tasks"""
    
    def __init__(self):
        self.root = Path(__file__).parent.parent
    
    def run(self, cmd: str, description: str = None) -> bool:
        """Run command with optional description"""
        if description:
            print(f"🔄 {description}")
        
        try:
            subprocess.run(cmd, shell=True, check=True, cwd=self.root)
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Command failed: {cmd}")
            return False
    
    def install(self):
        """Install project in development mode"""
        return self.run("pip install -e .", "Installing in development mode")
    
    def install_dev(self):
        """Install development dependencies"""
        return self.run("pip install -e .[dev]", "Installing with dev dependencies")
    
    def install_all(self):
        """Install all optional dependencies"""
        return self.run("pip install -e .[all]", "Installing with all dependencies")
    
    def test(self):
        """Run tests"""
        return self.run("python -m pytest", "Running tests")
    
    def test_cov(self):
        """Run tests with coverage"""
        return self.run("python -m pytest --cov=wara9a --cov-report=html", 
                       "Running tests with coverage")
    
    def format(self):
        """Format code"""
        success = self.run("python -m black .", "Formatting with black")
        success &= self.run("python -m isort .", "Sorting imports")
        return success
    
    def lint(self):
        """Run linting"""
        success = self.run("python -m flake8 wara9a", "Running flake8")
        success &= self.run("python -m mypy wara9a", "Running mypy")  
        return success
    
    def demo(self):
        """Run demo"""
        return self.run("python demo.py", "Running demo")
    
    def clean(self):
        """Clean build artifacts"""
        import shutil
        patterns = ["build", "dist", "*.egg-info", "__pycache__", 
                   ".pytest_cache", "htmlcov", ".coverage"]
        
        for pattern in patterns:
            for path in self.root.glob(f"**/{pattern}"):
                if path.exists():
                    if path.is_dir():
                        shutil.rmtree(path)
                    else:
                        path.unlink()
                    print(f"🗑️  Removed: {path}")
    
    def check(self):
        """Run all quality checks"""
        print("🔍 Running all quality checks...")
        success = self.format()
        success &= self.lint()
        success &= self.test()
        
        if success:
            print("🎉 All checks passed!")
        else:
            print("❌ Some checks failed")
        return success


def main():
    """Main CLI entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Wara9a development tasks")
    parser.add_argument("command", nargs="?", default="help",
                       choices=["install", "install-dev", "install-all", 
                               "test", "test-cov", "format", "lint", 
                               "demo", "clean", "check", "help"])
    
    args = parser.parse_args()
    runner = TaskRunner()
    
    if args.command == "help":
        print("Available commands:")
        print("  install      Install project in development mode")
        print("  install-dev  Install with development dependencies")
        print("  install-all  Install with all optional dependencies")
        print("  test         Run tests")
        print("  test-cov     Run tests with coverage")
        print("  format       Format code (black + isort)")
        print("  lint         Run linting (flake8 + mypy)")
        print("  demo         Run demo script")
        print("  clean        Clean build artifacts")
        print("  check        Run all quality checks")
        return
    
    method = getattr(runner, args.command.replace("-", "_"))
    success = method()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
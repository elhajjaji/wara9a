@echo off
REM Wara9a development task runner for Windows
REM Usage: dev.bat [command]

if "%1"=="" goto help
if "%1"=="help" goto help
if "%1"=="install" goto install
if "%1"=="install-dev" goto install-dev
if "%1"=="install-full" goto install-full
if "%1"=="test" goto test
if "%1"=="format" goto format
if "%1"=="lint" goto lint
if "%1"=="clean" goto clean
if "%1"=="demo" goto demo
if "%1"=="check" goto check

echo Unknown command: %1
goto help

:help
echo Wara9a Development Commands:
echo.
echo   install      Install basic dependencies
echo   install-dev  Install development dependencies  
echo   install-full Install all dependencies
echo   test         Run tests
echo   format       Format code (black + isort)
echo   lint         Run linting (flake8 + mypy)
echo   clean        Clean build artifacts
echo   demo         Run demo script
echo   check        Run all quality checks
echo.
goto end

:install
echo Installing basic dependencies...
pip install -r requirements.txt
goto end

:install-dev
echo Installing development dependencies...
pip install -r requirements-dev.txt
pip install -e .
goto end

:install-full
echo Installing all dependencies...
pip install -r requirements-full.txt
pip install -e .
goto end

:test
echo Running tests...
python -m pytest
goto end

:format
echo Formatting code...
python -m black wara9a tests demo.py scripts/
python -m isort wara9a tests demo.py scripts/
goto end

:lint
echo Running linting...
python -m flake8 wara9a tests
python -m mypy wara9a
goto end

:clean
echo Cleaning build artifacts...
python scripts/dev.py clean
goto end

:demo
echo Running demo...
python demo.py
goto end

:check
echo Running all quality checks...
python scripts/dev.py check
goto end

:end
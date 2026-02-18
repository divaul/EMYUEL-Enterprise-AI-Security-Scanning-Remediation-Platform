@echo off
REM EMYUEL Quick Setup Script for Windows with Smart Dependency Management

echo ================================================
echo   EMYUEL Security Scanner - Quick Setup
echo   with Auto Dependency Management
echo ================================================
echo.

REM Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.10 or higher from python.org
    exit /b 1
)

echo [OK] Python found
python --version
echo.

REM Create virtual environment
echo Creating virtual environment...
if exist venv (
    echo Virtual environment already exists, skipping creation
) else (
    python -m venv venv
    echo [OK] Virtual environment created
)
echo.

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip first
echo Upgrading pip to latest version...
python -m pip install --upgrade pip --quiet
echo [OK] pip upgraded
echo.

REM Install packaging for version comparison
echo Installing dependency management tools...
python -m pip install packaging --quiet
echo [OK] Tools installed
echo.

REM Check system tools first
echo ================================================
echo   Checking System Tools and Frameworks
echo ================================================
echo.
python check_system_tools.py
echo.

REM Run smart dependency checker
echo ================================================
echo   Checking and Managing Python Dependencies
echo ================================================
echo.
python check_dependencies.py

if errorlevel 1 (
    echo.
    echo [WARNING] Some dependencies had issues
    echo Attempting full installation from requirements.txt...
    pip install -r requirements.txt
)

echo.
REM Check cybersecurity tools
echo ================================================
echo   Checking Cybersecurity Tools
echo ================================================
echo.
python check_security_tools.py
echo.

echo.
echo ================================================
echo   Setup Complete!
echo ================================================
echo.
echo To use EMYUEL:
echo   1. Activate the virtual environment:
echo      venv\Scripts\activate.bat
echo.
echo   2. Run GUI (Recommended):
echo      python -m gui.emyuel_gui
echo.
echo   3. Run CLI:
echo      python -m cli.emyuel_cli scan --target /path/to/code
echo.
echo   4. Configure API keys in GUI or CLI:
echo      python -m cli.emyuel_cli config --provider openai
echo.
echo Features:
echo   * Quick Scan - URL-based scanning + 79 external tools
echo   * Advanced Scan - Comprehensive scanning with tool presets
echo   * External Tools - Nmap, Nuclei, SQLMap, Subfinder, etc.
echo   * Pipeline Chains - Auto-chain tools (subfinder-httprobe)
echo   * AI Analysis - Natural language security testing
echo   * Reports - PDF/HTML with severity breakdown
echo   * Database - Scan history with persistent storage
echo.
echo ================================================

pause

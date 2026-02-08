@echo off
REM EMYUEL Quick Setup Script for Windows

echo ================================================
echo   EMYUEL Security Scanner - Quick Setup
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
echo.

REM Create virtual environment
echo Creating virtual environment...
python -m venv venv

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

echo.
echo ================================================
echo   Setup Complete!
echo ================================================
echo.
echo To use EMYUEL:
echo   1. Activate the virtual environment:
echo      venv\Scripts\activate.bat
echo.
echo   2. Run CLI:
echo      python -m cli.emyuel_cli scan --target /path/to/code
echo.
echo   3. Run GUI:
echo      python -m gui.emyuel_gui
echo.
echo   4. Configure API keys:
echo      python -m cli.emyuel_cli config --provider openai
echo.
echo ================================================

pause

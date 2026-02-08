#!/bin/bash
# EMYUEL Quick Setup Script for Linux

echo "================================================"
echo "  EMYUEL Security Scanner - Quick Setup"
echo "================================================"
echo ""

# Check Python installation
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3 is not installed"
    echo "Please install Python 3.10 or higher"
    exit 1
fi

echo "[OK] Python found: $(python3 --version)"
echo ""

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "================================================"
echo "  Setup Complete!"
echo "================================================"
echo ""
echo "To use EMYUEL:"
echo "  1. Activate the virtual environment:"
echo "     source venv/bin/activate"
echo ""
echo "  2. Run CLI:"
echo "     python -m cli.emyuel_cli scan --target /path/to/code"
echo ""
echo "  3. Run GUI:"
echo "     python -m gui.emyuel_gui"
echo ""
echo "  4. Configure API keys:"
echo "     python -m cli.emyuel_cli config --provider openai"
echo ""
echo "================================================"

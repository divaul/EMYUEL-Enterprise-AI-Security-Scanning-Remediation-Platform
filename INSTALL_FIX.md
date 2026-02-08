# Installation Fix - Requirements.txt Encoding Error

## Problem Solved ✅

**Error:** `Invalid requirement: 'b\x00e\x00a\x00u...' (UTF-16 encoding issue)`

**Solution:** Recreated `requirements.txt` with proper UTF-8 encoding.

---

## Install Dependencies Now

```bash
# In Kali Linux
cd ~/EMYUEL-Enterprise-AI-Security-Scanning-Remediation-Platform
source venv/bin/activate
pip install -r requirements.txt
```

Should work now without errors!

---

## If You Still Get Errors

### Error: Some packages fail to install
Try installing in groups:

```bash
# Core dependencies first
pip install rich click pydantic python-dotenv requests

# LLM APIs
pip install openai google-generativeai anthropic

# Web scanning
pip install aiohttp beautifulsoup4 lxml

# GUI (if needed)
pip install PyQt5

# All others
pip install -r requirements.txt
```

### On Kali Linux: Missing system packages
Some packages need system libraries:

```bash
# For weasyprint (PDF generation)
sudo apt-get install -y build-essential python3-dev python3-pip \
    libcairo2 libpango-1.0-0 libpangocairo-1.0-0 \
    libgdk-pixbuf2.0-0 libffi-dev shared-mime-info

# For lxml
sudo apt-get install -y libxml2-dev libxslt1-dev

# For Pillow
sudo apt-get install -y libjpeg-dev zlib1g-dev
```

---

## Quick Test After Installation

```bash
# Test GUI
python -m gui.emyuel_gui

# Test CLI
python -m cli.emyuel_cli --help
```

---

## Minimum Required for Scanner

If you just want to test the scanner (not GUI):

```bash
pip install openai aiohttp beautifulsoup4 lxml rich
```

Then configure API key and run:
```bash
python -m cli.emyuel_cli config --provider openai --key sk-YOUR_KEY
python -m cli.emyuel_cli scan --target https://example.com
```

---

## Files Fixed

- ✅ `requirements.txt` - Recreated with UTF-8 encoding
- ✅ `gui/emyuel_gui.py` - Added missing typing imports
- ✅ All scanner components created and integrated

Scanner is ready to use! 🚀

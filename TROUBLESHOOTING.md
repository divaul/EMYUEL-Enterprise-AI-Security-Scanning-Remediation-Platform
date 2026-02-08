# EMYUEL Troubleshooting Guide

## Common Issues and Solutions

### 1. GUI Error: "no display name and no $DISPLAY environment variable"

**Error Message:**
```
_tkinter.TclError: no display name and no $DISPLAY environment variable
```

**Cause:**
GUI requires an X display server, which is not available in:
- SSH sessions without X11 forwarding
- Headless Linux systems
- WSL without X server
- Virtual machines without desktop environment

**Solutions:**

#### ✅ Solution 1: Use CLI Mode (Recommended for Kali Linux)

```bash
# CLI doesn't require display
python -m cli.emyuel_cli scan --target /path/to/code
python -m cli.emyuel_cli config --provider openai
python -m cli.emyuel_cli list
python -m cli.emyuel_cli report --scan-id scan_123
```

**Advantages:**
- No display required
- Lighter resource usage
- Better for automation/scripting
- Perfect for Kali Linux penetration testing workflow

#### ✅ Solution 2: Enable X11 Forwarding (Remote Access)

**For SSH access:**

```bash
# From your local machine (Windows/Mac/Linux):
ssh -X username@kali-ip-address

# Or with compression for better performance:
ssh -XC username@kali-ip-address

# Verify DISPLAY is set:
echo $DISPLAY
# Should show something like: localhost:10.0

# Now run GUI:
python -m gui.emyuel_gui
```

**For Windows users (PuTTY):**
1. Install X server (Xming or VcXsrv)
2. Start X server
3. In PuTTY: Connection → SSH → X11 → Enable X11 forwarding
4. Set X display location: `localhost:0`

**For Mac users:**
1. Install XQuartz: `brew install --cask xquartz`
2. Restart Mac
3. SSH with: `ssh -X user@kali-machine`

#### ✅ Solution 3: Virtual Display (Headless)

```bash
# Install xvfb
sudo apt update
sudo apt install xvfb

# Run GUI with virtual display
xvfb-run python -m gui.emyuel_gui

# Or set DISPLAY manually
export DISPLAY=:99
Xvfb :99 -screen 0 1024x768x24 &
python -m gui.emyuel_gui
```

#### ✅ Solution 4: Install Desktop Environment

```bash
# Install lightweight desktop
sudo apt install kali-desktop-xfce

# Or LXDE for minimal resources
sudo apt install lxde

# Start desktop
startx

# Then run GUI
python -m gui.emyuel_gui
```

#### ✅ Solution 5: VNC Server

```bash
# Install VNC server
sudo apt install tigervnc-standalone-server

# Start VNC server
vncserver :1

# Connect with VNC client from your local machine
# Then run GUI in VNC session
python -m gui.emyuel_gui
```

---

### 2. ModuleNotFoundError: No module named 'libs.api_key_manager'

**Error Message:**
```
ModuleNotFoundError: No module named 'libs.api_key_manager'
```

**Solution:**

The stub files should already be created. If you still see this error:

```bash
# Verify stub files exist
ls -la libs/api_key_manager.py
ls -la libs/scanner_state.py
ls -la services/scanner_core.py

# If missing, they should be created automatically
# Or manually check MODULE_FIX.md

# Test imports
python3 -c "from libs.api_key_manager import APIKeyManager; print('OK')"
python3 -c "from libs.scanner_state import StateManager; print('OK')"
```

---

### 3. Permission Denied for ~/.emyuel/

**Error Message:**
```
PermissionError: [Errno 13] Permission denied: '~/.emyuel/states'
```

**Solution:**

```bash
# Fix permissions
mkdir -p ~/.emyuel/states ~/.emyuel/cache
chmod 755 ~/.emyuel
chmod 755 ~/.emyuel/states
chmod 755 ~/.emyuel/cache

# Or remove and recreate
rm -rf ~/.emyuel
mkdir -p ~/.emyuel/states ~/.emyuel/cache
```

---

### 4. API Key Errors

**Error: Quota Exceeded**
```
openai.error.RateLimitError: You exceeded your current quota
```

**Solution:**
- Add backup API key
- Switch to different provider (Gemini/Claude)
- Check OpenAI billing dashboard

```bash
# Configure backup key
python -m cli.emyuel_cli config --provider gemini

# Or edit .env file directly
nano .env
# Add: GOOGLE_AI_API_KEY=your_backup_key
```

**Error: Invalid API Key**
```
openai.error.AuthenticationError: Incorrect API key provided
```

**Solution:**
```bash
# Reconfigure API key
python -m cli.emyuel_cli config --provider openai

# Verify key format:
# OpenAI: sk-...
# Google: AI...
# Anthropic: sk-ant-...
```

---

### 5. Dependencies Installation Fails

**Error:**
```
ERROR: Could not build wheels for X
```

**Solution:**

```bash
# Install build dependencies
sudo apt update
sudo apt install -y \
    python3-dev \
    build-essential \
    libssl-dev \
    libffi-dev \
    libpq-dev \
    gcc

# Upgrade pip
pip install --upgrade pip setuptools wheel

# Reinstall requirements
pip install -r requirements.txt
```

---

### 6. Python Version Issues

**Error:**
```
SyntaxError: invalid syntax
```

**Solution:**

```bash
# Check Python version (need 3.10+)
python3 --version

# Install Python 3.11 on Kali
sudo apt update
sudo apt install python3.11 python3.11-venv

# Use specific version
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

### 7. Virtual Environment Not Activating

**Issue:** Commands not found after activation

**Solution:**

```bash
# Deactivate first
deactivate

# Recreate venv
rm -rf venv
python3 -m venv venv

# Activate properly
source venv/bin/activate

# Verify
which python
# Should show: /path/to/emyuel/venv/bin/python

# Reinstall
pip install -r requirements.txt
```

---

## Best Practices for Kali Linux

### ✅ Recommended Setup

1. **Use CLI mode** for security scanning
2. **Run as regular user** (not root unless necessary)
3. **Keep API keys in .env** (never commit to git)
4. **Use virtual environment** always

### ✅ Typical Kali Workflow

```bash
# 1. Activate environment
cd ~/EMYUEL-*
source venv/bin/activate

# 2. Configure once
python -m cli.emyuel_cli config --provider openai

# 3. Run scans
python -m cli.emyuel_cli scan --target /var/www/webapp

# 4. Generate reports
python -m cli.emyuel_cli report --scan-id scan_20260208 --format html

# 5. View in browser (if X available)
firefox reports/*/report.html
```

---

## Getting Help

If you're still stuck:

1. **Check logs**: `cat logs/emyuel.log`
2. **Read docs**: `DOKUMENTASI_PROGRAM.md` (Bahasa Indonesia)
3. **Verify setup**: Run `./setup-kali.sh` again
4. **GitHub Issues**: Report bugs with full error trace

---

## Quick Reference

| Problem | Solution |
|---------|----------|
| No display for GUI | Use CLI mode or enable X11 |
| Module not found | Check stub files in libs/ |
| Permission denied | Fix ~/.emyuel permissions |
| API quota exceeded | Switch provider or add backup key |
| Build errors | Install python3-dev and build-essential |
| Python too old | Install Python 3.10+ |
| Venv issues | Recreate virtual environment |

---

**For Kali Linux users:** CLI mode is recommended as it doesn't require X server and is more suitable for penetration testing workflows!

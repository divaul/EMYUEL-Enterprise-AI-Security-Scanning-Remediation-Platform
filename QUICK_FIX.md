# Quick Setup Fix

## Error Fixed: `NameError: name 'List' is not defined`

**Problem:** Missing typing imports in GUI

**Solution:** Already fixed! Updated `gui/emyuel_gui.py` with proper imports.

---

## Testing the GUI

```bash
# Activate virtual environment (if using one)
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Install missing dependencies (if any)
pip install beautifulsoup4 lxml

# Test GUI
python -m gui.emyuel_gui
```

Should launch without errors now!

---

## If You Get Import Errors

### Error: `ModuleNotFoundError: No module named 'beautifulsoup4'`
```bash
pip install beautifulsoup4 lxml
```

### Error: `ModuleNotFoundError: No module named 'openai'`
```bash
pip install openai google-generativeai anthropic
```

### Error: `ModuleNotFoundError: No module named 'aiohttp'`
```bash
pip install aiohttp
```

### Install All at Once
```bash
pip install -r requirements.txt
```

---

## Configure API Key Before Scanning

After GUI launches:
1. Go to **"API Keys"** tab
2. Enter your API key:
   - OpenAI: starts with `sk-`
   - Gemini: starts with `AI`
   - Claude: starts with `sk-ant-`
3. Click **"Test"** (checks format only)
4. Click **"Save"**

---

## First Scan Test

1. Go to **"Advanced Scan"** tab
2. Enter target:
   - URL: `https://example.com`
   - OR directory: Browse to your code folder
3. Click **"Start Scan"**
4. Wait for results (real scan, not demo!)

---

## Expected Results

✅ **Scanner initializes** → Console shows initialization
✅ **Scan runs** → Progress bar updates
✅ **Findings display** → Real vulnerabilities (if found)
✅ **No warnings** → No more "stub/demo" messages

---

## Common Issues

**Scan takes too long:**
- Normal! LLM analysis is slow
- Web scans: 30s-2min
- Code scans: 1-5min

**No findings:**
- Target might be secure
- Or scan didn't cover that area
- Try different modules

**Error: "API key not configured":**
- Go to API Keys tab
- Save a valid key
- Try again

---

## Need Help?

See full docs:
- [Setup Guide](REAL_SCANNER_SETUP.md)
- [Walkthrough](scanner_walkthrough.md)
- [Troubleshooting](TROUBLESHOOTING.md)

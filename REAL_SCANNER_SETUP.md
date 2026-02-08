# Real Scanner Installation Guide

## Quick Start

Install the required dependencies for the real scanner:

```bash
pip install --upgrade beautifulsoup4 lxml
```

The following dependencies should already be installed (check requirements.txt):
- `openai>=1.0.0` - For OpenAI GPT-4 analysis
- `google-generativeai>=0.3.0` - For Google Gemini
- `anthropic>=0.18.0` - For Claude
- `aiohttp>=3.9.0` - For async HTTP requests
- `rich>=13.0.0` - For CLI output

## API Keys Required

Before running scans, configure at least one LLM provider:

### Option 1: GUI Configuration
1. Run GUI: `python gui/emyuel_gui.py`
2. Go to "API Keys" tab
3. Enter your API key
4. Click "Test" then "Save"

### Option 2: CLI Configuration  
```bash
python -m cli.emyuel_cli config --provider openai --key sk-YOUR_KEY_HERE
```

### Option 3: Manual Setup
Create `~/.emyuel/api_keys.json`:
```json
{
  "openai": [{"key": "sk-YOUR_KEY", "is_backup": false}],
  "gemini": [{"key": "YOUR_GEMINI_KEY", "is_backup": false}],
"claude": [{"key": "sk-ant-YOUR_KEY", "is_backup": false}]
}
```

## Running Real Scans

### Web Scan
```bash
# CLI
python -m cli.emyuel_cli scan --target https://example.com --modules xss,sqli

# GUI
python gui/emyuel_gui.py
# Enter URL in target field, click "Start Scan"
```

### Code Scan
```bash
# CLI
python -m cli.emyuel_cli scan --target /path/to/code --modules secrets,sqli

# GUI
python gui/emyuel_gui.py
# Browse to directory, click "Start Scan"
```

## What Changed

✅ **Removed:**
- All "demo" and "stub" warnings
- Fake scan progress simulation
- Placeholder results

✅ **Added:**
- Real LLM-powered analysis
- Web scanner with crawling
- Code scanner with pattern matching
- Actual vulnerability detection
- Real findings with evidence and remediation

## Expected Behavior

1. **Scan starts** → Scanner initializes with your API key
2. **Web scan** → Crawls pages, tests forms, checks headers
3. **Code scan** → Parses files, detects patterns, LLM analysis
4. **Results** → Real vulnerabilities with:
   - Severity (Critical/High/Medium/Low)
   - Description
   - Evidence (code snippets, URLs)
   - Remediation advice

## Troubleshooting

**Error: "API key not configured"**
→ Run `config` command or add key via GUI

**Error: "ImportError: No module named 'beautifulsoup4'"**
→ Run: `pip install beautifulsoup4 lxml`

**Error: "Scanner core directory not found"**
→ Ensure `services/scanner-core/` directory exists

**Scan is slow**
→ Normal! LLM analysis takes time. Reduce `max_pages` for web scans.

## Performance Notes

- **Web scans:** ~30s-2min for small sites (< 50 pages)
- **Code scans:** ~1-5min for 100-500 files
- **LLM calls:** ~2-5s per request

Uses GPT-4 by default, falls back to GPT-3.5-turbo if quota exceeded.

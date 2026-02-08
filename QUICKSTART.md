# EMYUEL Quick Start Guide

## Installation

### Windows
```batch
# Run setup script
setup.bat
```

### Linux
```bash
# Make setup script executable
chmod +x setup.sh


# Run setup script
./setup.sh
```

## Configuration

### Set up API keys
```bash
# Method 1: Environment variables (add to .env file)
OPENAI_API_KEY=sk-...
GOOGLE_AI_API_KEY=AI...
ANTHROPIC_API_KEY=sk-ant-...

# Method 2: CLI configuration
python -m cli.emyuel_cli config --provider openai

# Method 3: Auto-prompt (will ask when needed)
```

## Usage

### CLI Mode

#### Full Scan
```bash
python -m cli.emyuel_cli scan --target /path/to/your/code
```

#### Targeted Scan
```bash
python -m cli.emyuel_cli scan --target /path/to/code --modules sqli,xss,ssrf
```

#### Advanced Options
```bash
python -m cli.emyuel_cli scan \
  --target /path/to/code \
  --modules sqli,xss,rce,auth \
  --provider gemini \
  --profile comprehensive \
  --output-dir ./my-reports
```

#### Pause and Resume
```bash
# Start scan, press Ctrl+C to pause
python -m cli.emyuel_cli scan --target /path/to/code
# ^C (paused)

# List resumable scans
python -m cli.emyuel_cli list

# Resume
python -m cli.emyuel_cli resume --scan-id scan_20260130_123456
```

#### Generate Reports
```bash
# Generate all formats (JSON, HTML, PDF)
python -m cli.emyuel_cli report --scan-id scan_20260130_123456 --format all

# Single format
python -m cli.emyuel_cli report --scan-id scan_20260130_123456 --format pdf
```

### GUI Mode

```bash
python -m gui.emyuel_gui
```

**GUI Features:**
1. Click "Browse" to select target directory
2. Choose scan mode (Full / Targeted)
3. Select LLM provider (OpenAI / Gemini / Claude)
4. Choose profile (Quick / Standard / Comprehensive)
5. Click "Start Scan"
6. Monitor progress in real-time
7. View vulnerability statistics
8. Generate reports

## API Key Error Handling

EMYUEL automatically handles API errors:

### Scenario 1: Quota Exhausted
```
[DETECTED] Quota exceeded for primary key
[ACTION] Switching to backup key automatically
[RESULT] Scan continues without interruption
```

### Scenario 2: Invalid Key
```
[DETECTED] Invalid API key
[PROMPT] Please enter a valid OpenAI API key: _
[ACTION] Validates new key and retries
```

### Scenario 3: Rate Limit
```
[DETECTED] Rate limit exceeded
[ACTION] Waiting 60 seconds before retry...
[OPTION] Enter new key or wait? [w/k]: _
```

## Report Structure

All reports are saved to:
```
reports/
└── 20260130_123456_example_com/
    ├── report.json          # Machine-readable
    ├── report.html          # Interactive web report
    ├── report.pdf           # Executive summary
    ├── metadata.json        # Scan metadata
    └── evidence/            # Screenshots, logs
```

## Examples

### Example 1: Quick Security Check
```bash
# Quick scan with OpenAI
python -m cli.emyuel_cli scan \
  --target ./my-web-app \
  --profile quick \
  --provider openai
```

### Example 2: Comprehensive Audit
```bash
# Full scan with all modules
python -m cli.emyuel_cli scan \
  --target ./enterprise-app \
  --profile comprehensive \
  --provider claude
```

### Example 3: Specific Vulnerability Testing
```bash
# Test only SQL injection and XSS
python -m cli.emyuel_cli scan \
  --target ./api-server \
  --modules sqli,xss \
  --provider gemini \
  --profile standard
```

## Troubleshooting

### Issue: "Python not found"
**Solution:** Install Python 3.10+ from python.org and add to PATH

### Issue: "API key not configured"
**Solution:** Run `python -m cli.emyuel_cli config --provider openai`

### Issue: "Module not found"
**Solution:** Activate virtual environment: `venv\Scripts\activate` (Windows) or `source venv/bin/activate` (Linux)

### Issue: GUI doesn't open
**Solution:** 
- Windows: Ensure tkinter is installed (comes with Python)
- Linux: Install tk package: `sudo apt-get install python3-tk`

## Support

- **Documentation:** See [README.md](file:///c:/Users/divau/Documents/cyber/emyuel/README.md)
- **Implementation Plan:** See [implementation_plan.md](file:///C:/Users/divau/.gemini/antigravity/brain/3bec1fec-09d3-4276-b9ca-fff91f7c3822/implementation_plan.md)
- **Detailed Walkthrough:** See [walkthrough.md](file:///C:/Users/divau/.gemini/antigravity/brain/3bec1fec-09d3-4276-b9ca-fff91f7c3822/walkthrough.md)

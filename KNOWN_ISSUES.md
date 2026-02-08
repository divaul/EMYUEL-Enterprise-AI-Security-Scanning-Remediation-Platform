# Known Issues & Limitations

## Current Implementation Status

### ✅ Implemented & Working
- ✅ Modern GUI with tabs (Quick Scan, Advanced, API Keys, Results)
- ✅ Natural Language Processing (English + Indonesian)
- ✅ CLI with query command
- ✅ API Key management (save/load)
- ✅ Target detection (URL vs Directory)
- ✅ Scan mode selection (Full/Targeted)
- ✅ Console logging
- ✅ Progress indicators

### ⚠️ Partially Implemented / Stub
- ⚠️ **API Key Validation** - Only format validation, not live API test
- ⚠️ **Scanner Core** - Demo/stub implementation only
- ⚠️ **Scan Execution** - Shows demo progress, no real scanning
- ⚠️ **Report Generation** - Stub only
- ⚠️ **Pause/Resume** - UI exists but not functional

### ❌ Not Implemented
- ❌ Actual vulnerability scanning engine
- ❌ LLM integration for analysis
- ❌ Real-time vulnerability detection
- ❌ Report file generation
- ❌ Database storage
- ❌ Multi-threading for scans

---

## Known Issues

### Issue 1: API Key Test Always Shows "Valid"

**Problem:**
All API keys (OpenAI, Gemini, Claude) show as "valid" regardless of actual validity.

**Why:**
The `test_api_key()` function only validates key **format**, not actual API connectivity.

**Current Behavior:**
- OpenAI key: Must start with `sk-`
- Gemini key: Must start with `AI`
- Claude key: Must start with `sk-ant-`

**Workaround:**
- Keys are tested when you actually run a scan
- GUI will show warning: "⚠ Format OK (Not tested live)"

**Fix Status:** ✅ **FIXED** - Now shows format validation only with clear warning

---

### Issue 2: GUI Freezes/Hangs During Scan

**Problem:**
GUI becomes unresponsive when clicking "Start Scan".

**Why:**
Demo scan runs in main thread, blocking UI updates.

**Current Behavior:**
- Repeated log messages
- UI freeze
- Cannot click buttons

**Workaround:**
- Close and restart GUI
- Use CLI instead of GUI for now

**Fix Status:** ✅ **FIXED** - Scan now shows warning dialog and runs non-blocking demo

---

### Issue 3: Scanner Core Not Implemented

**Problem:**
No actual vulnerability scanning happens.

**Impact:**
- Scans don't find real vulnerabilities
- Only demo/stub output
- No real security analysis

**Current Behavior:**
- Shows "Scanner core not implemented" warning
- Demo progress bar
- Random fake findings
- "Coming soon" message

**Status:** 🔧 **Work in Progress**

Real scanner implementation requires:
1. LLM API integration (OpenAI/Gemini/Claude)
2. Code analysis engine
3. Vulnerability detection patterns
4. Report generation pipeline

---

## Workarounds & Best Practices

### For API Key Testing

**Instead of GUI test:**
```python
# Test OpenAI manually
python -c "import openai; openai.api_key='sk-...'; print(openai.Model.list())"

# Test Gemini manually  
python -c "import google.generativeai as genai; genai.configure(api_key='AI...'); print('OK')"

# Test Claude manually
python -c "import anthropic; client = anthropic.Anthropic(api_key='sk-ant-...'); print('OK')"
```

### For Scanning

**Use CLI instead of GUI for now:**
```bash
# CLI doesn't freeze (shows warning clearly)
python -m cli.emyuel_cli scan --target https://example.com --all
```

### For Development

**Testing GUI without scanner:**
```python
# The GUI works for:
- Natural language query parsing ✅
- API key save/load ✅
- Target input ✅
- Mode selection ✅

# Just don't click "Start Scan" expecting real results
```

---

## Error Messages Explained

### "Scanner Core Not Implemented"

**Message:**
```
⚠️ WARNING: Scanner core is not fully implemented yet.

This will only show a demo/stub scan.

Continue with demo?
```

**Meaning:**
- No real scanning will happen
- Only demonstration UI/UX
- Progress bar is fake
- Findings are random

**Action:**
- Click "No" to cancel
- Click "Yes" to see demo UI

---

### "Format OK (Not tested live)"

**Message in API Key status:**
```
⚠ Format OK (Not tested live)
```

**Meaning:**
- Key format is correct (starts with right prefix)
- Length is reasonable
- But NOT tested against actual API

**Action:**
- Save the key anyway
- It will be tested when you run a real scan (future)

---

## Roadmap

### Phase 1: Core Scanner (**Next Priority**)
- [ ] Implement LLM API calls
- [ ] Add code analysis engine
- [ ] Create vulnerability detection patterns
- [ ] Integrate with existing UI

### Phase 2: Real API Validation
- [ ] Add live API key testing
- [ ] Show quota/usage info
- [ ] Handle rate limits

### Phase 3: Advanced Features
- [ ] Multi-threaded scanning
- [ ] Real pause/resume
- [ ] Database storage
- [ ] Advanced reporting

---

## Getting Help

**If you encounter:**
1. **GUI freeze** → Fixed! Restart GUI and see warning dialog
2. **All keys valid** → Fixed! Now shows format validation warning
3. **No real scan** → Expected! Scanner core coming soon
4. **Other issues** → Check logs: `logs/emyuel.log`

**For latest updates:**
- Check `walkthrough.md` for implementation status
- Check `task.md` for development progress

---

## Development Notes

**For contributors:**

The codebase is structured to make scanner integration easy:

```python
# In gui/emyuel_gui.py - Replace stub with real scanner
def start_advanced_scan(self):
    # Current: Shows demo
    # TODO: Call actual scanner with:
    #   - self.scanner = ScannerCore(config)
    #   - await self.scanner.scan(target, modules)
    #   - Update UI with real results
```

**Integration points ready:**
- ✅ Config management
- ✅ Progress callbacks
- ✅ Result display
- ✅ Report generation hooks

**Just need:**
- ❌ Actual scanner implementation
- ❌ LLM integration code
- ❌ Vulnerability patterns

---

Last Updated: 2026-02-08

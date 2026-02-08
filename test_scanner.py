#!/usr/bin/env python3
"""
Quick Scanner Test - Verify scanner installation

This script tests if the scanner core can be imported and initialized.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

print("=" * 60)
print("EMYUEL Scanner - Import Test")
print("="  * 60)

# Test 1: Import scanner_core
print("\n[1] Testing scanner_core import...")
try:
    from services.scanner_core import ScannerCore
    print("    ✅ scanner_core imported successfully")
except ImportError as e:
    print(f"    ❌ Failed to import scanner_core: {e}")
    print("\n    Check:")
    print("    - services/scanner-core/ directory exists")
    print("    - services/scanner-core/scanner_core.py exists")
    sys.exit(1)

# Test 2: Check scanner-core files
print("\n[2] Checking scanner-core directory...")
scanner_core_dir = project_root / "services" / "scanner-core"
required_files = [
    "scanner_core.py",
    "llm_analyzer.py",
    "web_scanner.py",
    "code_scanner.py",
    "api_key_manager.py"
]

for filename in required_files:
    filepath = scanner_core_dir / filename
    if filepath.exists():
        print(f"    ✅ {filename}")
    else:
        print(f"    ❌ {filename} NOT FOUND")

# Test 3: Initialize scanner
print("\n[3] Testing scanner initialization...")
try:
    scanner = ScannerCore({})
    print("    ✅ Scanner initialized successfully")
except Exception as e:
    print(f"    ❌ Failed to initialize scanner: {e}")
    print("\n    This is OK if you haven't configured API keys yet")

# Test 4: Check dependencies
print("\n[4] Checking dependencies...")
dependencies = {
    "aiohttp": "Web scanning",
    "beautifulsoup4": "HTML parsing",
    "openai": "OpenAI LLM (optional)",
    "google.generativeai": "Gemini LLM (optional)",
    "anthropic": "Claude LLM (optional)"
}

for module, purpose in dependencies.items():
    try:
        __import__(module.replace(".", "/"))
        print(f"    ✅ {module} - {purpose}")
    except ImportError:
        print(f"    ❌ {module} - {purpose} (install with: pip install {module.split('.')[0]})")

print("\n" + "=" * 60)
print("Scanner Status:")
print("=" * 60)

# Check if all critical dependencies are met
critical_missing = []
for module in ["aiohttp", "beautifulsoup4"]:
    try:
        __import__(module)
    except ImportError:
        critical_missing.append(module)

if critical_missing:
    print("❌ INCOMPLETE: Missing critical dependencies")
    print(f"   Run: pip install {' '.join(critical_missing)}")
else:
    print("✅ READY: Scanner core is properly installed")
    print("\nNext steps:")
    print("1. Configure API key: python -m cli.emyuel_cli config --provider openai --key YOUR_KEY")
    print("2. Run scan: python -m cli.emyuel_cli scan --target https://example.com")
    print("3. Or use GUI: python -m gui.emyuel_gui")

print("=" * 60)

#!/usr/bin/env python3
"""
EMYUEL Cybersecurity Tools Manager
Dynamically checks all tools from gui/security_tools.py registry.
Provides install instructions per OS and auto-install on Linux/Kali.
"""

import subprocess
import sys
import os
import platform
import shutil
from pathlib import Path
from typing import Dict, List, Tuple


# ---------------------------------------------------------------------------
# Import the SINGLE SOURCE OF TRUTH — gui/security_tools.py
# ---------------------------------------------------------------------------
def _load_registry() -> Dict:
    """Import SECURITY_TOOLS from gui.security_tools (handles path issues)."""
    project_root = Path(__file__).resolve().parent
    sys.path.insert(0, str(project_root))
    try:
        from gui.security_tools import SECURITY_TOOLS
        return SECURITY_TOOLS
    except ImportError:
        # Fallback: exec the file directly
        ns = {}
        exec(open(project_root / "gui" / "security_tools.py", encoding="utf-8").read(), ns)
        return ns["SECURITY_TOOLS"]


# ---------------------------------------------------------------------------
# Tools that are Python libraries, NOT CLI binaries — skip PATH check
# ---------------------------------------------------------------------------
PYTHON_LIBRARY_TOOLS = {
    'aiohttp', 'requests', 'beautifulsoup', 'scrapy', 'httpx_pkg',
    'google_genai', 'seclists',
}

# Tools that are GUI-only / interactive — no CLI auto-run
INTERACTIVE_TOOLS = {
    'burpsuite', 'mitmproxy', 'openvas',
}

# Reporting platforms — need separate server, not a CLI binary
PLATFORM_TOOLS = {
    'dradis', 'faraday', 'defectdojo',
}

SKIP_PATH_CHECK = PYTHON_LIBRARY_TOOLS | INTERACTIVE_TOOLS | PLATFORM_TOOLS


class SecurityToolsManager:
    """Manage cybersecurity tools based on the central registry."""

    def __init__(self):
        self.os_type = platform.system().lower()
        self.is_windows = self.os_type == 'windows'
        self.is_linux = self.os_type == 'linux'
        self.is_mac = self.os_type == 'darwin'
        self.is_kali = self._is_kali_linux()
        self.registry = _load_registry()

    # ---- helpers ----
    @staticmethod
    def _is_kali_linux() -> bool:
        try:
            with open('/etc/os-release') as f:
                return 'kali' in f.read().lower()
        except Exception:
            return False

    def _resolve_binary(self, tool_id: str, info: Dict) -> str | None:
        """Find the binary on PATH (or common Go/Cargo dirs)."""
        cmd = info.get('check_cmd', tool_id)
        # shutil.which is the safest cross-platform check
        found = shutil.which(cmd)
        if found:
            return found

        # Check common Go / Cargo locations
        extra_dirs = []
        home = Path.home()
        go_bin = os.environ.get('GOBIN') or str(home / 'go' / 'bin')
        extra_dirs.append(go_bin)
        extra_dirs.append(str(home / '.cargo' / 'bin'))
        if self.is_linux or self.is_mac:
            extra_dirs += ['/usr/local/bin', '/snap/bin', str(home / '.local' / 'bin')]

        for d in extra_dirs:
            candidate = Path(d) / cmd
            if candidate.exists():
                return str(candidate)
            if self.is_windows:
                candidate_exe = Path(d) / f"{cmd}.exe"
                if candidate_exe.exists():
                    return str(candidate_exe)
        return None

    def _install_instruction(self, info: Dict) -> str:
        """Get the install instruction for the current OS."""
        # Custom install takes precedence
        custom = info.get('install_custom')
        apt = info.get('install_apt')
        pip = info.get('install_pip')

        if self.is_kali or self.is_linux:
            if apt:
                return f"sudo apt-get install {apt} -y"
            elif pip:
                return f"pip install {pip}"
            elif custom:
                return custom
        elif self.is_mac:
            if apt:
                return f"brew install {apt}"
            elif pip:
                return f"pip install {pip}"
            elif custom:
                return custom
        elif self.is_windows:
            if pip:
                return f"pip install {pip}"
            elif custom:
                return custom
            elif apt:
                return f"Install via WSL: sudo apt-get install {apt} -y"

        return custom or (f"pip install {pip}" if pip else "See tool website")

    # ---- main logic ----
    def check_all_tools(self, debug: bool = False) -> Dict[str, Dict]:
        """Check all tools, grouped by category."""
        debug = debug or os.environ.get('EMYUEL_DEBUG', '').lower() in ('1', 'true')

        print("🔐 Checking cybersecurity tools...")
        if debug:
            print("    (Debug mode enabled)")
        print()

        # Group by category
        categories: Dict[str, list] = {}
        for tid, info in self.registry.items():
            cat = info.get('category', 'Other')
            categories.setdefault(cat, []).append((tid, info))

        results = {}
        cli_total = 0
        cli_installed = 0
        lib_count = 0
        skip_count = 0

        for cat in sorted(categories):
            tools = categories[cat]
            print(f"📁 {cat}")

            for tid, info in tools:
                name = info.get('name', tid)
                desc = info.get('desc', '')
                icon = info.get('icon', '🔧')

                if tid in PYTHON_LIBRARY_TOOLS:
                    # Python library — check import instead
                    pkg = info.get('install_pip') or tid
                    try:
                        __import__(pkg.replace('-', '_').split('[')[0])
                        status_sym = "✅"
                        installed = True
                    except ImportError:
                        status_sym = "📦"
                        installed = False
                    lib_count += 1
                    tag = " (Python lib)"
                elif tid in INTERACTIVE_TOOLS | PLATFORM_TOOLS:
                    status_sym = "ℹ️ "
                    installed = None  # N/A
                    skip_count += 1
                    tag = " (interactive/platform)"
                else:
                    # CLI binary — check PATH
                    path = self._resolve_binary(tid, info)
                    installed = path is not None
                    cli_total += 1
                    if installed:
                        cli_installed += 1
                        status_sym = "✅"
                    else:
                        status_sym = "❌"
                    tag = ""

                    if debug and path:
                        print(f"      PATH: {path}")

                print(f"  {status_sym} {icon} {name:18s} — {desc}{tag}")

                results[tid] = {
                    'installed': installed,
                    'name': name,
                    'category': cat,
                    'desc': desc,
                }

            print()

        # Summary
        print("=" * 64)
        print(f"  CLI tools: {cli_installed}/{cli_total} installed")
        print(f"  Python libs: {lib_count} (checked via import)")
        print(f"  Interactive/platform: {skip_count} (manual setup)")
        print("=" * 64)
        print()

        return results

    def auto_install_linux(self, tool_id: str, info: Dict) -> bool:
        """Attempt apt/pip install on Linux."""
        apt = info.get('install_apt')
        pip = info.get('install_pip')

        if apt:
            cmd = f"sudo apt-get install {apt} -y"
        elif pip:
            cmd = f"pip install {pip}"
        else:
            custom = info.get('install_custom', '')
            if custom.startswith('go install') or custom.startswith('cargo install'):
                cmd = custom
            else:
                print(f"  ⚠️  No auto-install for {tool_id}: {custom}")
                return False

        print(f"  ⏳ Running: {cmd}")
        try:
            result = subprocess.run(cmd, shell=True, text=True, timeout=180)
            if result.returncode == 0:
                print(f"  ✅ {tool_id} installed")
                return True
            else:
                print(f"  ❌ Failed (exit {result.returncode})")
                return False
        except subprocess.TimeoutExpired:
            print(f"  ❌ Timed out")
            return False
        except Exception as e:
            print(f"  ❌ Error: {e}")
            return False

    def print_install_instructions(self, results: Dict[str, Dict]):
        """Print install instructions for missing CLI tools."""
        missing = []
        for tid, status in results.items():
            if status['installed'] is False and tid not in SKIP_PATH_CHECK:
                missing.append(tid)

        if not missing:
            return

        print("=" * 64)
        print("  📦 Installation Instructions for Missing Tools")
        print("=" * 64)
        print()

        for tid in sorted(missing):
            info = self.registry[tid]
            instr = self._install_instruction(info)
            print(f"  {info.get('icon', '🔧')} {info.get('name', tid)}")
            print(f"     {instr}")
            print()


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------
def main():
    print("""
╔══════════════════════════════════════════════════════════════╗
║    EMYUEL Cybersecurity Tools Manager  (v2 — auto-sync)    ║
║    Reads tool list from gui/security_tools.py registry     ║
╚══════════════════════════════════════════════════════════════╝
    """)

    manager = SecurityToolsManager()

    # OS banner
    if manager.is_kali:
        print("🐉 Detected: Kali Linux — many tools pre-installed")
    elif manager.is_linux:
        print(f"🐧 Detected: Linux")
    elif manager.is_windows:
        print("🪟 Detected: Windows")
    elif manager.is_mac:
        print("🍎 Detected: macOS")
    print()

    # Check
    results = manager.check_all_tools()

    # Count missing CLI tools
    missing_cli = [
        tid for tid, s in results.items()
        if s['installed'] is False and tid not in SKIP_PATH_CHECK
    ]

    # Auto-install prompt (Linux only)
    if manager.is_linux and missing_cli:
        print(f"Found {len(missing_cli)} missing CLI tool(s).")
        print("Auto-install missing tools? (requires sudo for apt)")
        resp = input("Install now? (y/N): ").strip().lower()

        if resp == 'y':
            print()
            ok = fail = 0
            for tid in missing_cli:
                info = manager.registry[tid]
                print(f"📦 {info.get('name', tid)}")
                if manager.auto_install_linux(tid, info):
                    ok += 1
                else:
                    fail += 1
                print()

            print("=" * 64)
            print(f"  ✅ Installed: {ok}  |  ❌ Failed: {fail}")
            print("=" * 64)
            print()

            if ok > 0:
                print("🔄 Re-checking after installation...\n")
                results = manager.check_all_tools()
        else:
            print("⏭️  Skipping auto-install\n")

    # Print install instructions
    manager.print_install_instructions(results)

    # Final
    if not missing_cli:
        print("✅ All CLI security tools are available!")
        print("   EMYUEL is ready for security testing! 🚀\n")
        return 0
    else:
        print(f"⚠️  {len(missing_cli)} CLI tool(s) still missing — some scans may skip them")
        print("   Missing tools will be silently skipped during scans.\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())

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
    'google_genai', 'openai_sdk', 'anthropic_sdk',
}

# Tools that are GUI-only / interactive — no CLI auto-run
INTERACTIVE_TOOLS = {
    'burpsuite', 'mitmproxy', 'openvas',
}

# Reporting platforms — need separate server, not a CLI binary
PLATFORM_TOOLS = {
    'dradis', 'faraday', 'defectdojo',
}

# Resource-only entries — no binary to check
RESOURCE_TOOLS = {
    'seclists',
}

SKIP_PATH_CHECK = PYTHON_LIBRARY_TOOLS | INTERACTIVE_TOOLS | PLATFORM_TOOLS | RESOURCE_TOOLS


class SecurityToolsManager:
    """Manage cybersecurity tools based on the central registry."""

    def __init__(self):
        self.os_type = platform.system().lower()
        self.is_windows = self.os_type == 'windows'
        self.is_linux = self.os_type == 'linux'
        self.is_mac = self.os_type == 'darwin'
        self.is_kali = self._is_kali_linux()
        self.registry = _load_registry()
        self._go_installed = False  # track whether we already installed Go

    # ---- helpers ----
    @staticmethod
    def _is_kali_linux() -> bool:
        try:
            with open('/etc/os-release') as f:
                return 'kali' in f.read().lower()
        except Exception:
            return False

    def _get_env_with_paths(self) -> dict:
        """Return env dict that includes Go/Cargo bin in PATH."""
        env = os.environ.copy()
        home = Path.home()
        extra = [
            '/usr/local/go/bin',
            str(home / 'go' / 'bin'),
            str(home / '.cargo' / 'bin'),
            '/usr/local/bin',
            str(home / '.local' / 'bin'),
        ]
        env['PATH'] = ':'.join(extra) + ':' + env.get('PATH', '')
        env['GOPATH'] = str(home / 'go')
        return env

    def _resolve_binary(self, tool_id: str, info: Dict) -> str | None:
        """Find the binary on PATH (or common Go/Cargo dirs)."""
        cmd = info.get('check_cmd') or info.get('check_cmd', tool_id)
        if cmd is None:
            return None
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
            extra_dirs += ['/usr/local/go/bin', '/usr/local/bin', '/snap/bin',
                           str(home / '.local' / 'bin')]

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

    # ---- Go runtime installer ----
    def _ensure_go_runtime(self) -> bool:
        """Install Go runtime if not already available."""
        env = self._get_env_with_paths()
        # Check if go is already in any known location
        go_paths = ['/usr/local/go/bin/go', str(Path.home() / 'go' / 'bin' / 'go')]
        if shutil.which('go', path=env.get('PATH', '')) is not None:
            return True
        for gp in go_paths:
            if Path(gp).exists():
                return True

        if self._go_installed:
            return False  # We already tried and it failed

        print()
        print("  🐹 Go runtime not found — installing Go 1.22.4...")
        try:
            cmds = [
                'wget -q https://go.dev/dl/go1.22.4.linux-amd64.tar.gz -O /tmp/go.tar.gz',
                'sudo rm -rf /usr/local/go',
                'sudo tar -C /usr/local -xzf /tmp/go.tar.gz',
                'rm -f /tmp/go.tar.gz',
            ]
            for cmd in cmds:
                r = subprocess.run(cmd, shell=True, timeout=120)
                if r.returncode != 0:
                    print(f"  ❌ Go install step failed: {cmd}")
                    self._go_installed = True
                    return False

            # Verify
            result = subprocess.run(
                '/usr/local/go/bin/go version', shell=True,
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                print(f"  ✅ {result.stdout.strip()}")
                # Update current process PATH
                os.environ['PATH'] = '/usr/local/go/bin:' + str(Path.home() / 'go' / 'bin') + ':' + os.environ.get('PATH', '')
                self._go_installed = True
                return True
            else:
                print("  ❌ Go verification failed")
                self._go_installed = True
                return False
        except Exception as e:
            print(f"  ❌ Go install error: {e}")
            self._go_installed = True
            return False

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
                    pkg = info.get('install_pip') or tid
                    mod = pkg.replace('-', '_').split('[')[0]
                    try:
                        __import__(mod)
                        status_sym = "✅"
                        installed = True
                    except ImportError:
                        status_sym = "📦"
                        installed = False
                    lib_count += 1
                    tag = " (Python lib)"
                elif tid in RESOURCE_TOOLS:
                    found = any(Path(d).is_dir() for d in [
                        '/usr/share/seclists', '/opt/seclists',
                        str(Path.home() / 'SecLists'),
                    ])
                    status_sym = "✅" if found else "📦"
                    installed = found
                    skip_count += 1
                    tag = " (resource)"
                elif tid in INTERACTIVE_TOOLS | PLATFORM_TOOLS:
                    status_sym = "ℹ️ "
                    installed = None  # N/A
                    skip_count += 1
                    tag = " (interactive/platform)"
                else:
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
        """Attempt to install a tool on Linux using the best available method."""
        apt = info.get('install_apt')
        pip = info.get('install_pip')
        custom = info.get('install_custom', '')

        # Determine install command
        if apt:
            cmd = f"sudo apt-get install {apt} -y"
        elif pip:
            cmd = f"pip install {pip}"
        elif custom:
            # For Go-based tools, ensure Go runtime is available first
            if 'go install' in custom:
                if not self._ensure_go_runtime():
                    print("  ⚠️  Go runtime not available — skipping")
                    return False
            # For Cargo-based tools, auto-install Rust if needed
            elif custom.startswith('cargo install'):
                if not shutil.which('cargo'):
                    print("  🦀 Cargo not found — installing Rust...")
                    try:
                        r = subprocess.run(
                            'curl --proto "=https" --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y',
                            shell=True, timeout=300, env=self._get_env_with_paths()
                        )
                        if r.returncode != 0:
                            print("  ❌ Rust install failed — skipping")
                            return False
                        os.environ['PATH'] = str(Path.home() / '.cargo' / 'bin') + ':' + os.environ.get('PATH', '')
                        print("  ✅ Rust installed")
                    except Exception as e:
                        print(f"  ❌ Rust install error: {e}")
                        return False
            # For npm-based tools, auto-install nodejs+npm if needed
            elif 'npm install' in custom:
                if not shutil.which('npm'):
                    print("  📦 npm not found — installing Node.js + npm...")
                    try:
                        r = subprocess.run('sudo apt-get install -y nodejs npm', shell=True, timeout=120)
                        if r.returncode != 0:
                            print("  ❌ npm install failed — skipping")
                            return False
                        print("  ✅ Node.js + npm installed")
                    except Exception as e:
                        print(f"  ❌ npm install error: {e}")
                        return False
            # For gem-based tools, auto-install ruby if needed
            elif custom.startswith('gem install'):
                if not shutil.which('gem'):
                    print("  💎 gem not found — installing Ruby...")
                    try:
                        r = subprocess.run('sudo apt-get install -y ruby ruby-dev', shell=True, timeout=120)
                        if r.returncode != 0:
                            print("  ❌ Ruby install failed — skipping")
                            return False
                        print("  ✅ Ruby installed")
                    except Exception as e:
                        print(f"  ❌ Ruby install error: {e}")
                        return False

            cmd = custom
        else:
            print(f"  ⚠️  No install method available for {tool_id}")
            return False

        print(f"  ⏳ Running: {cmd}")
        try:
            env = self._get_env_with_paths()
            result = subprocess.run(
                cmd, shell=True, text=True, timeout=300,
                env=env,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            )
            if result.returncode == 0:
                print(f"  ✅ {tool_id} installed")
                return True
            else:
                # Show last line of stderr for debugging
                err = (result.stderr or '').strip().split('\n')
                last_err = err[-1] if err else ''
                print(f"  ❌ Failed (exit {result.returncode})")
                if last_err:
                    print(f"     {last_err[:120]}")
                return False
        except subprocess.TimeoutExpired:
            print(f"  ❌ Timed out (5 min)")
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
║    EMYUEL Cybersecurity Tools Manager  (v3 — auto-sync)    ║
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

    # Print install instructions for remaining missing
    manager.print_install_instructions(results)

    # Re-count after potential installs
    missing_cli = [
        tid for tid, s in results.items()
        if s['installed'] is False and tid not in SKIP_PATH_CHECK
    ]

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

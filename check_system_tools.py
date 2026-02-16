#!/usr/bin/env python3
"""
EMYUEL System Tools Manager
Checks, downloads, and updates required system tools and frameworks
"""

import subprocess
import sys
import platform
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class SystemToolsManager:
    """Manage system tools and frameworks"""
    
    def __init__(self):
        self.os_type = platform.system().lower()  # 'windows', 'linux', 'darwin'
        self.is_windows = self.os_type == 'windows'
        self.is_linux = self.os_type == 'linux'
        self.is_mac = self.os_type == 'darwin'
        
        # Required tools with their check commands and install hints
        self.required_tools = {
            'git': {
                'check_cmd': ['git', '--version'],
                'min_version': '2.0.0',
                'install_windows': 'Download from: https://git-scm.com/download/win',
                'install_linux': 'sudo apt-get install git -y',
                'install_mac': 'brew install git',
                'priority': 'high'
            },
            'curl': {
                'check_cmd': ['curl', '--version'],
                'min_version': '7.0.0',
                'install_windows': 'Included in Windows 10+',
                'install_linux': 'sudo apt-get install curl -y',
                'install_mac': 'brew install curl',
                'priority': 'medium'
            },
            'node': {
                'check_cmd': ['node', '--version'],
                'min_version': '14.0.0',
                'install_windows': 'Download from: https://nodejs.org/',
                'install_linux': 'curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash - && sudo apt-get install nodejs -y',
                'install_mac': 'brew install node',
                'priority': 'low',
                'optional': True
            },
            'npm': {
                'check_cmd': ['npm', '--version'],
                'min_version': '6.0.0',
                'install_windows': 'Comes with Node.js',
                'install_linux': 'Comes with Node.js',
                'install_mac': 'Comes with Node.js',
                'priority': 'low',
                'optional': True
            }
        }
    
    def run_command(self, cmd: List[str], capture: bool = True) -> Tuple[bool, str]:
        """Run a command and return success status and output"""
        try:
            result = subprocess.run(
                cmd,
                capture_output=capture,
                text=True,
                timeout=10
            )
            return result.returncode == 0, result.stdout.strip()
        except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
            return False, ""
    
    def extract_version(self, version_string: str) -> Optional[str]:
        """Extract version number from version string"""
        import re
        
        # Common patterns: v1.2.3, 1.2.3, version 1.2.3
        patterns = [
            r'v?(\d+\.\d+\.\d+)',
            r'(\d+\.\d+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, version_string)
            if match:
                return match.group(1)
        
        return None
    
    def compare_versions(self, current: str, minimum: str) -> bool:
        """Compare version strings"""
        try:
            from packaging import version
            return version.parse(current) >= version.parse(minimum)
        except Exception:
            # Fallback to simple comparison
            current_parts = [int(x) for x in current.split('.')]
            min_parts = [int(x) for x in minimum.split('.')]
            
            # Pad shorter version
            while len(current_parts) < len(min_parts):
                current_parts.append(0)
            while len(min_parts) < len(current_parts):
                min_parts.append(0)
            
            return current_parts >= min_parts
    
    def check_tool(self, tool_name: str, tool_info: Dict) -> Tuple[bool, Optional[str]]:
        """
        Check if a tool is installed and meets version requirements
        
        Returns:
            (installed, version)
        """
        success, output = self.run_command(tool_info['check_cmd'])
        
        if not success:
            return False, None
        
        version = self.extract_version(output)
        return True, version
    
    def check_all_tools(self) -> Dict[str, Dict]:
        """Check all required tools"""
        results = {}
        
        print("🔧 Checking system tools...")
        print()
        
        for tool_name, tool_info in self.required_tools.items():
            installed, version = self.check_tool(tool_name, tool_info)
            is_optional = tool_info.get('optional', False)
            
            status = {
                'installed': installed,
                'version': version,
                'optional': is_optional,
                'meets_requirements': False
            }
            
            if installed and version:
                min_version = tool_info.get('min_version')
                if min_version:
                    meets_req = self.compare_versions(version, min_version)
                    status['meets_requirements'] = meets_req
                    
                    if meets_req:
                        print(f"  ✅ {tool_name}: {version}")
                    else:
                        print(f"  ⚠️  {tool_name}: {version} (requires >= {min_version})")
                else:
                    status['meets_requirements'] = True
                    print(f"  ✅ {tool_name}: {version}")
            else:
                if is_optional:
                    print(f"  ℹ️  {tool_name}: Not installed (optional)")
                else:
                    print(f"  ❌ {tool_name}: Not installed")
            
            results[tool_name] = status
        
        return results
    
    def auto_install_linux(self, tool_name: str, tool_info: Dict) -> bool:
        """Attempt to auto-install tool on Linux"""
        install_cmd = tool_info.get('install_linux', '')
        
        if not install_cmd or 'sudo apt-get' not in install_cmd:
            return False
        
        print(f"  Installing {tool_name}...")
        
        try:
            # Run install command
            result = subprocess.run(
                install_cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode == 0:
                print(f"  ✅ {tool_name} installed successfully")
                return True
            else:
                print(f"  ❌ Failed to install {tool_name}")
                return False
                
        except Exception as e:
            print(f"  ❌ Error installing {tool_name}: {e}")
            return False
    
    def print_install_instructions(self, results: Dict[str, Dict]):
        """Print installation instructions for missing tools"""
        missing = []
        outdated = []
        
        for tool_name, status in results.items():
            if not status['installed']:
                if not status['optional']:
                    missing.append(tool_name)
            elif not status['meets_requirements']:
                outdated.append(tool_name)
        
        if not missing and not outdated:
            return
        
        print()
        print("="*60)
        print("  Installation Instructions")
        print("="*60)
        print()
        
        if missing:
            print("Missing tools:")
            print()
            for tool_name in missing:
                tool_info = self.required_tools[tool_name]
                print(f"📦 {tool_name}")
                
                if self.is_windows:
                    print(f"   {tool_info['install_windows']}")
                elif self.is_linux:
                    print(f"   {tool_info['install_linux']}")
                elif self.is_mac:
                    print(f"   {tool_info['install_mac']}")
                print()
        
        if outdated:
            print("Outdated tools (update recommended):")
            print()
            for tool_name in outdated:
                tool_info = self.required_tools[tool_name]
                current_ver = results[tool_name]['version']
                min_ver = tool_info.get('min_version', 'latest')
                print(f"🔄 {tool_name}: {current_ver} → {min_ver}+")
                print()
    
    def check_python_version(self) -> bool:
        """Check if Python version is adequate"""
        print("🐍 Checking Python version...")
        
        version_info = sys.version_info
        current = f"{version_info.major}.{version_info.minor}.{version_info.micro}"
        
        if version_info >= (3, 10):
            print(f"  ✅ Python {current}")
            return True
        else:
            print(f"  ⚠️  Python {current} (requires >= 3.10)")
            return False


def main():
    """Main entry point"""
    print("""
╔══════════════════════════════════════════════════════════╗
║         EMYUEL System Tools Manager                     ║
║  Check, install, and update system dependencies         ║
╚══════════════════════════════════════════════════════════╝
    """)
    
    manager = SystemToolsManager()
    
    # Check Python version
    python_ok = manager.check_python_version()
    print()
    
    # Check all tools
    results = manager.check_all_tools()
    print()
    
    # Count status
    total = len(results)
    installed = sum(1 for r in results.values() if r['installed'])
    meets_req = sum(1 for r in results.values() if r['meets_requirements'])
    missing_required = sum(1 for name, r in results.items() 
                          if not r['installed'] and not r['optional'])
    
    print("="*60)
    print(f"Status: {meets_req}/{total} OK | {installed - meets_req} outdated | {missing_required} missing")
    print("="*60)
    print()
    
    # Auto-install on Linux if requested
    if manager.is_linux and missing_required > 0:
        print("Would you like to auto-install missing tools? (requires sudo)")
        response = input("Install now? (y/N): ").strip().lower()
        
        if response == 'y':
            print()
            print("Installing missing tools...")
            print()
            
            for tool_name, status in results.items():
                if not status['installed'] and not status['optional']:
                    tool_info = manager.required_tools[tool_name]
                    manager.auto_install_linux(tool_name, tool_info)
            
            # Re-check after installation
            print()
            print("Re-checking after installation...")
            print()
            results = manager.check_all_tools()
    
    # Print install instructions
    manager.print_install_instructions(results)
    
    # Final verdict
    print()
    if python_ok and missing_required == 0:
        print("✅ All required system tools are available!")
        print()
        print("Next step: Run Python dependency checker")
        print("  python check_dependencies.py")
        return 0
    else:
        if not python_ok:
            print("⚠️  Python version is below recommended (3.10+)")
        if missing_required > 0:
            print(f"⚠️  {missing_required} required tool(s) missing")
        print()
        print("Please install missing tools and run again")
        return 1


if __name__ == "__main__":
    sys.exit(main())

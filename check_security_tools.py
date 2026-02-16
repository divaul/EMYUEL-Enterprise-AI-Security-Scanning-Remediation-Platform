#!/usr/bin/env python3
"""
EMYUEL Cybersecurity Tools Manager
Checks, downloads, and updates essential security testing tools
"""

import subprocess
import sys
import platform
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class SecurityToolsManager:
    """Manage cybersecurity tools and frameworks"""
    
    def __init__(self):
        self.os_type = platform.system().lower()
        self.is_windows = self.os_type == 'windows'
        self.is_linux = self.os_type == 'linux'
        self.is_mac = self.os_type == 'darwin'
        self.is_kali = self._is_kali_linux()
        
        # Essential security tools
        self.security_tools = {
            'nmap': {
                'check_cmd': ['nmap', '-V'],  # Use -V instead of --version
                'description': 'Network scanner and port discovery',
                'install_windows': 'Download from: https://nmap.org/download.html',
                'install_linux': 'sudo apt-get install nmap -y',
                'install_kali': 'Pre-installed on Kali, or: sudo apt-get install nmap -y',
                'install_mac': 'brew install nmap',
                'priority': 'high',
                'category': 'reconnaissance'
            },
            'sqlmap': {
                'check_cmd': ['sqlmap', '-h'],  # Use -h instead of --version
                'description': 'SQL injection detection and exploitation',
                'install_windows': 'pip install sqlmap or download from sqlmap.org',
                'install_linux': 'sudo apt-get install sqlmap -y',
                'install_kali': 'Pre-installed on Kali',
                'install_mac': 'brew install sqlmap',
                'priority': 'high',
                'category': 'exploitation'
            },
            'nikto': {
                'check_cmd': ['nikto', '-Version'],  # Already correct
                'description': 'Web server vulnerability scanner',
                'install_windows': 'Install via Perl + download from cirt.net/Nikto2',
                'install_linux': 'sudo apt-get install nikto -y',
                'install_kali': 'Pre-installed on Kali',
                'install_mac': 'brew install nikto',
                'priority': 'medium',
                'category': 'scanning'
            },
            'wpscan': {
                'check_cmd': ['wpscan', '--version'],
                'description': 'WordPress security scanner',
                'install_windows': 'gem install wpscan',
                'install_linux': 'sudo apt-get install wpscan -y or gem install wpscan',
                'install_kali': 'Pre-installed on Kali, or: sudo apt-get install wpscan -y',
                'install_mac': 'brew install wpscan',
                'priority': 'medium',
                'category': 'scanning',
                'optional': True
            },
            'hydra': {
                'check_cmd': ['hydra', '-h'],
                'description': 'Network logon cracker (brute force)',
                'install_windows': 'Download from: github.com/vanhauser-thc/thc-hydra',
                'install_linux': 'sudo apt-get install hydra -y',
                'install_kali': 'Pre-installed on Kali',
                'install_mac': 'brew install hydra',
                'priority': 'medium',
                'category': 'brute-force',
                'optional': True
            },
            'john': {
                'check_cmd': ['john', '--version'],
                'description': 'John the Ripper - password cracker',
                'install_windows': 'Download from: www.openwall.com/john/',
                'install_linux': 'sudo apt-get install john -y',
                'install_kali': 'Pre-installed on Kali',
                'install_mac': 'brew install john',
                'priority': 'low',
                'category': 'password-cracking',
                'optional': True
            },
            'hashcat': {
                'check_cmd': ['hashcat', '--version'],
                'description': 'Advanced password recovery',
                'install_windows': 'Download from: hashcat.net/hashcat/',
                'install_linux': 'sudo apt-get install hashcat -y',
                'install_kali': 'Pre-installed on Kali',
                'install_mac': 'brew install hashcat',
                'priority': 'low',
                'category': 'password-cracking',
                'optional': True
            },
            'dirb': {
                'check_cmd': ['dirb'],
                'description': 'Web content scanner (directory bruteforce)',
                'install_windows': 'Install via WSL or download binary',
                'install_linux': 'sudo apt-get install dirb -y',
                'install_kali': 'Pre-installed on Kali',
                'install_mac': 'brew install dirb',
                'priority': 'medium',
                'category': 'reconnaissance',
                'optional': True
            },
            'gobuster': {
                'check_cmd': ['gobuster', 'version'],
                'description': 'Directory/DNS/VHost busting tool',
                'install_windows': 'Download from: github.com/OJ/gobuster',
                'install_linux': 'sudo apt-get install gobuster -y',
                'install_kali': 'Pre-installed on Kali',
                'install_mac': 'brew install gobuster',
                'priority': 'medium',
                'category': 'reconnaissance',
                'optional': True
            }
        }
    
    def _is_kali_linux(self) -> bool:
        """Check if running on Kali Linux"""
        if not self.is_linux:
            return False
        
        try:
            with open('/etc/os-release', 'r') as f:
                content = f.read().lower()
                return 'kali' in content
        except Exception:
            return False
    
    def run_command(self, cmd: List[str], capture: bool = True) -> Tuple[bool, str]:
        """Run a command and return success status and output"""
        try:
            result = subprocess.run(
                cmd,
                capture_output=capture,
                text=True,
                timeout=10,
                stderr=subprocess.STDOUT
            )
            return result.returncode == 0, result.stdout.strip() if result.stdout else ""
        except subprocess.TimeoutExpired:
            return False, "Timeout"
        except FileNotFoundError:
            return False, "Not found"
        except Exception as e:
            return False, str(e)
    
    def check_tool(self, tool_name: str, tool_info: Dict) -> bool:
        """Check if a security tool is installed using 'which' command"""
        # Use 'which' command - more reliable than running the tool itself
        success, output = self.run_command(['which', tool_name])
        
        # If 'which' succeeds and returns a path, tool is installed
        if success and output and '/' in output:
            return True
        
        # Fallback: try the original check command
        success2, output2 = self.run_command(tool_info['check_cmd'])
        return success2
    
    def check_all_tools(self) -> Dict[str, Dict]:
        """Check all security tools"""
        results = {}
        
        print("🔐 Checking cybersecurity tools...")
        print()
        
        # Group by category
        categories = {}
        for tool_name, tool_info in self.security_tools.items():
            category = tool_info.get('category', 'other')
            if category not in categories:
                categories[category] = []
            categories[category].append((tool_name, tool_info))
        
        # Check each category
        for category, tools in sorted(categories.items()):
            print(f"📁 {category.upper().replace('-', ' ')}")
            
            for tool_name, tool_info in tools:
                installed = self.check_tool(tool_name, tool_info)
                is_optional = tool_info.get('optional', False)
                
                status = {
                    'installed': installed,
                    'optional': is_optional,
                    'priority': tool_info.get('priority', 'low'),
                    'category': category
                }
                
                # Status symbol
                if installed:
                    symbol = "✅"
                elif is_optional:
                    symbol = "ℹ️ "
                else:
                    symbol = "❌"
                
                # Description
                desc = tool_info.get('description', '')
                optional_tag = " (optional)" if is_optional else ""
                
                print(f"  {symbol} {tool_name:12} - {desc}{optional_tag}")
                
                results[tool_name] = status
            
            print()
        
        return results
    
    def auto_install_linux(self, tool_name: str, tool_info: Dict) -> bool:
        """Attempt to auto-install security tool on Linux"""
        install_key = 'install_kali' if self.is_kali else 'install_linux'
        install_cmd = tool_info.get(install_key, '')
        
        # Extract actual install command (ignore "Pre-installed" part)
        # Example: "Pre-installed on Kali, or: sudo apt-get install nmap -y"
        if 'pre-installed' in install_cmd.lower():
            # Check if there's an "or:" part with actual install command
            if ' or:' in install_cmd.lower() or ' or ' in install_cmd.lower():
                # Extract command after "or:"
                parts = install_cmd.split(' or')
                if len(parts) > 1:
                    install_cmd = parts[-1].strip().lstrip(':').strip()
                    print(f"  ℹ️  {tool_name} claims to be pre-installed, but not found")
                    print(f"     Attempting installation anyway...")
                else:
                    print(f"  ⚠️  {tool_name} should be pre-installed on Kali")
                    print(f"     No install command available. Try: sudo apt-get update && sudo apt-get install {tool_name} -y")
                    return False
            else:
                # No "or" clause - try standard apt-get
                install_cmd = f"sudo apt-get install {tool_name} -y"
                print(f"  ℹ️  {tool_name} claims to be pre-installed, but not found")
                print(f"     Trying: {install_cmd}")
        
        if not install_cmd or 'sudo apt-get' not in install_cmd:
            print(f"  ⚠️  No auto-install available for {tool_name}")
            print(f"     Manual install: {install_cmd}")
            return False
        
        print(f"  ⏳ Installing {tool_name}...")
        
        try:
            # Run with live output for sudo prompt
            result = subprocess.run(
                install_cmd,
                shell=True,
                text=True,
                timeout=180  # 3 minutes max
            )
            
            if result.returncode == 0:
                print(f"  ✅ {tool_name} installed successfully")
                return True
            else:
                print(f"  ❌ Failed to install {tool_name} (exit code: {result.returncode})")
                print(f"     Try manually: {install_cmd}")
                return False
                
        except subprocess.TimeoutExpired:
            print(f"  ❌ Installation timed out for {tool_name}")
            return False
        except Exception as e:
            print(f"  ❌ Error installing {tool_name}: {e}")
            return False
    
    def print_install_instructions(self, results: Dict[str, Dict]):
        """Print installation instructions for missing tools"""
        missing_high = []
        missing_medium = []
        missing_low = []
        
        for tool_name, status in results.items():
            if not status['installed'] and not status['optional']:
                priority = status['priority']
                if priority == 'high':
                    missing_high.append(tool_name)
                elif priority == 'medium':
                    missing_medium.append(tool_name)
                else:
                    missing_low.append(tool_name)
        
        if not any([missing_high, missing_medium, missing_low]):
            return
        
        print("="*60)
        print("  Installation Instructions")
        print("="*60)
        print()
        
        if self.is_kali:
            print("💡 Running on Kali Linux - many tools are pre-installed")
            print("   If a tool shows as missing, try updating package list:")
            print("   sudo apt-get update")
            print()
        
        for priority, missing_list, emoji in [
            ('HIGH PRIORITY', missing_high, '🔴'),
            ('MEDIUM PRIORITY', missing_medium, '🟡'),
            ('LOW PRIORITY (Optional)', missing_low, '⚪')
        ]:
            if missing_list:
                print(f"{emoji} {priority}:")
                print()
                
                for tool_name in missing_list:
                    tool_info = self.security_tools[tool_name]
                    print(f"📦 {tool_name} - {tool_info['description']}")
                    
                    if self.is_windows:
                        print(f"   {tool_info['install_windows']}")
                    elif self.is_kali:
                        print(f"   {tool_info['install_kali']}")
                    elif self.is_linux:
                        print(f"   {tool_info['install_linux']}")
                    elif self.is_mac:
                        print(f"   {tool_info['install_mac']}")
                    print()


def main():
    """Main entry point"""
    print("""
╔══════════════════════════════════════════════════════════╗
║      EMYUEL Cybersecurity Tools Manager                 ║
║  Check and install essential security testing tools     ║
╚══════════════════════════════════════════════════════════╝
    """)
    
    manager = SecurityToolsManager()
    
    # Show system info
    if manager.is_kali:
        print("🐉 Detected: Kali Linux")
        print("   Many security tools should already be installed")
    elif manager.is_linux:
        print(f"🐧 Detected: Linux ({platform.system()})")
    elif manager.is_windows:
        print("🪟 Detected: Windows")
    elif manager.is_mac:
        print("🍎 Detected: macOS")
    
    print()
    
    # Check all tools
    results = manager.check_all_tools()
    
    # Count status
    total = len(results)
    installed = sum(1 for r in results.values() if r['installed'])
    missing_required = sum(1 for r in results.values() 
                          if not r['installed'] and not r['optional'])
    missing_optional = sum(1 for r in results.values() 
                          if not r['installed'] and r['optional'])
    
    print("="*60)
    print(f"Status: {installed}/{total} installed | {missing_required} required missing | {missing_optional} optional missing")
    print("="*60)
    print()
    
    # Auto-install on Linux if requested
    if manager.is_linux and missing_required > 0:
        print("Would you like to auto-install missing required tools?")
        print("(This requires sudo privileges)")
        response = input("Install now? (y/N): ").strip().lower()
        
        if response == 'y':
            print()
            print("="*60)
            print("  🔧 AUTO-INSTALLING MISSING REQUIRED TOOLS")
            print("="*60)
            print()
            print("⚠️  You may be prompted for your sudo password")
            print()
            
            installed_count = 0
            failed_count = 0
            
            for tool_name, status in results.items():
                if not status['installed'] and not status['optional']:
                    tool_info = manager.security_tools[tool_name]
                    
                    # Show what we're installing
                    install_key = 'install_kali' if manager.is_kali else 'install_linux'
                    install_cmd = tool_info.get(install_key, '')
                    
                    print(f"📦 {tool_name}")
                    print(f"   Command: {install_cmd}")
                    print()
                    
                    success = manager.auto_install_linux(tool_name, tool_info)
                    
                    if success:
                        installed_count += 1
                    else:
                        failed_count += 1
                    
                    print()
            
            # Summary
            print("="*60)
            print(f"  INSTALLATION SUMMARY")
            print("="*60)
            print(f"  ✅ Installed: {installed_count}")
            print(f"  ❌ Failed: {failed_count}")
            print("="*60)
            print()
            
            # Re-check after installation
            if installed_count > 0:
                print("🔄 Re-checking tools after installation...")
                print()
                results = manager.check_all_tools()
        else:
            print()
            print("⏭️  Skipping auto-installation")
            print("   You can install tools manually later")
            print()
    
    # Print install instructions
    manager.print_install_instructions(results)
    
    # Re-count after potential installation
    missing_required = sum(1 for r in results.values() 
                          if not r['installed'] and not r['optional'])
    
    # Final verdict
    print()
    if missing_required == 0:
        print("✅ All required security tools are available!")
        missing_optional = sum(1 for r in results.values() 
                              if not r['installed'] and r['optional'])
        if missing_optional > 0:
            print(f"ℹ️  {missing_optional} optional tool(s) not installed")
        print()
        print("EMYUEL is ready for security testing!")
        return 0
    else:
        print(f"⚠️  {missing_required} required security tool(s) still missing")
        print()
        print("⚠️  IMPORTANT: Some security scanning features will not work")
        print("   without these tools. Please install them manually:")
        print()
        
        for tool_name, status in results.items():
            if not status['installed'] and not status['optional']:
                tool_info = manager.security_tools[tool_name]
                install_key = 'install_kali' if manager.is_kali else 'install_linux'
                print(f"   • {tool_name}: {tool_info.get(install_key, 'N/A')}")
        
        print()
        print("⏭️  Setup will continue, but tool scans may fail")
        
        # Return non-zero to indicate tools are missing
        # But don't fail setup completely (return 1 instead of exit code > 1)
        return 1


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""
EMYUEL Dependency Manager
Automatically checks, installs, and updates required Python packages
"""

import subprocess
import sys
import json
from pathlib import Path
from typing import Dict, List, Tuple
import re


class DependencyManager:
    """Smart dependency management for EMYUEL"""
    
    def __init__(self, requirements_file: str = "requirements.txt"):
        self.requirements_file = Path(requirements_file)
        self.required_packages = {}
        self.installed_packages = {}
        
    def parse_requirements(self) -> Dict[str, str]:
        """Parse requirements.txt and extract package versions"""
        packages = {}
        
        if not self.requirements_file.exists():
            print(f"❌ {self.requirements_file} not found!")
            sys.exit(1)
        
        with open(self.requirements_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                
                # Skip comments and empty lines
                if not line or line.startswith('#'):
                    continue
                
                # Remove inline comments (e.g., "package>=1.0  # comment")
                line = line.split('#')[0].strip()
                
                # Parse package name and version
                match = re.match(r'^([a-zA-Z0-9_\-\[\]]+)([\><= !]+)([\d\.]+)', line)
                if match:
                    package_name = match.group(1)
                    operator = match.group(2)
                    version = match.group(3)
                    packages[package_name.lower()] = {
                        'name': package_name,
                        'operator': operator,
                        'version': version,
                        'requirement': line  # Clean line without comments
                    }
        
        self.required_packages = packages
        return packages
    
    def get_installed_packages(self) -> Dict[str, str]:
        """Get list of installed packages and their versions"""
        try:
            result = subprocess.run(
                [sys.executable, '-m', 'pip', 'list', '--format=json'],
                capture_output=True,
                text=True,
                check=True
            )
            
            packages = json.loads(result.stdout)
            installed = {}
            
            for pkg in packages:
                name = pkg['name'].lower()
                version = pkg['version']
                installed[name] = version
            
            self.installed_packages = installed
            return installed
            
        except Exception as e:
            print(f"⚠️  Warning: Could not get installed packages: {e}")
            return {}
    
    def compare_versions(self, installed: str, required: str, operator: str) -> bool:
        """Compare package versions"""
        from packaging import version
        
        try:
            inst_ver = version.parse(installed)
            req_ver = version.parse(required)
            
            if operator == '>=':
                return inst_ver >= req_ver
            elif operator == '==':
                return inst_ver == req_ver
            elif operator == '>':
                return inst_ver > req_ver
            elif operator == '<=':
                return inst_ver <= req_ver
            elif operator == '<':
                return inst_ver < req_ver
            else:
                return True
                
        except Exception:
            # If version parsing fails, assume it's okay
            return True
    
    def check_dependencies(self) -> Tuple[List[str], List[str], List[str]]:
        """
        Check which packages are missing, outdated, or OK
        
        Returns:
            (missing, outdated, ok)
        """
        missing = []
        outdated = []
        ok = []
        
        self.parse_requirements()
        self.get_installed_packages()
        
        print("📦 Checking dependencies...")
        print()
        
        for pkg_key, pkg_info in self.required_packages.items():
            pkg_name = pkg_info['name']
            required_ver = pkg_info['version']
            operator = pkg_info['operator']
            
            if pkg_key not in self.installed_packages:
                missing.append(pkg_info['requirement'])
                print(f"  ❌ {pkg_name}: Not installed")
            else:
                installed_ver = self.installed_packages[pkg_key]
                
                if self.compare_versions(installed_ver, required_ver, operator):
                    ok.append(pkg_name)
                    print(f"  ✅ {pkg_name}: {installed_ver}")
                else:
                    outdated.append(pkg_info['requirement'])
                    print(f"  ⚠️  {pkg_name}: {installed_ver} (requires {operator}{required_ver})")
        
        return missing, outdated, ok
    
    def install_package(self, requirement: str) -> bool:
        """Install a single package"""
        try:
            print(f"Installing {requirement}...")
            subprocess.run(
                [sys.executable, '-m', 'pip', 'install', requirement],
                check=True,
                capture_output=True
            )
            print(f"  ✅ Installed {requirement}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"  ❌ Failed to install {requirement}: {e}")
            return False
    
    def upgrade_package(self, requirement: str) -> bool:
        """Upgrade a single package"""
        try:
            print(f"Upgrading {requirement}...")
            subprocess.run(
                [sys.executable, '-m', 'pip', 'install', '--upgrade', requirement],
                check=True,
                capture_output=True
            )
            print(f"  ✅ Upgraded {requirement}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"  ❌ Failed to upgrade {requirement}: {e}")
            return False
    
    def install_all(self) -> bool:
        """Install all packages from requirements.txt"""
        try:
            print("📦 Installing all dependencies from requirements.txt...")
            subprocess.run(
                [sys.executable, '-m', 'pip', 'install', '-r', str(self.requirements_file)],
                check=True
            )
            print("✅ All dependencies installed!")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Installation failed: {e}")
            return False
    
    def upgrade_all(self) -> bool:
        """Upgrade all packages from requirements.txt"""
        try:
            print("🔄 Upgrading all dependencies...")
            subprocess.run(
                [sys.executable, '-m', 'pip', 'install', '--upgrade', '-r', str(self.requirements_file)],
                check=True
            )
            print("✅ All dependencies upgraded!")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Upgrade failed: {e}")
            return False
    
    def auto_fix(self) -> bool:
        """Automatically install missing and upgrade outdated packages"""
        missing, outdated, ok = self.check_dependencies()
        
        print()
        print("="*60)
        print(f"Missing: {len(missing)} | Outdated: {len(outdated)} | OK: {len(ok)}")
        print("="*60)
        print()
        
        success = True
        
        # Install missing packages
        if missing:
            print(f"📥 Installing {len(missing)} missing package(s)...")
            print()
            for requirement in missing:
                if not self.install_package(requirement):
                    success = False
            print()
        
        # Upgrade outdated packages
        if outdated:
            print(f"🔄 Upgrading {len(outdated)} outdated package(s)...")
            print()
            for requirement in outdated:
                if not self.upgrade_package(requirement):
                    success = False
            print()
        
        if not missing and not outdated:
            print("✅ All dependencies are up to date!")
        
        return success


def main():
    """Main entry point"""
    print("""
╔══════════════════════════════════════════════════════════╗
║         EMYUEL Dependency Manager                       ║
║  Auto-check, install, and update Python packages        ║
╚══════════════════════════════════════════════════════════╝
    """)
    
    manager = DependencyManager()
    
    # Check if packaging module is available
    try:
        import packaging
    except ImportError:
        print("Installing packaging module for version comparison...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'packaging'], check=True)
        print()
    
    # Auto-fix dependencies
    success = manager.auto_fix()
    
    print()
    if success:
        print("✅ Dependency management completed successfully!")
        print()
        print("Next steps:")
        print("  1. Configure API keys in .env or GUI")
        print("  2. Run: python -m gui.emyuel_gui")
        return 0
    else:
        print("⚠️  Some dependencies failed to install/upgrade")
        print("Please check the errors above and try again")
        return 1


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""
Quick diagnostic test for 'which' command
Run this to verify Python subprocess can detect tools
"""

import subprocess
import sys

def test_which(tool_name):
    """Test if 'which' command works for a tool"""
    print(f"\n{'='*60}")
    print(f"Testing: {tool_name}")
    print('='*60)
    
    # Test 1: which command
    try:
        result = subprocess.run(
            ['which', tool_name],
            capture_output=True,
            text=True,
            timeout=10,
            stderr=subprocess.STDOUT
        )
        
        print(f"Command: which {tool_name}")
        print(f"Exit code: {result.returncode}")
        print(f"Output: '{result.stdout.strip()}'")
        print(f"Success: {result.returncode == 0}")
        
        if result.returncode == 0 and result.stdout.strip() and '/' in result.stdout:
            print(f"✅ DETECTED: {tool_name} at {result.stdout.strip()}")
            return True
        else:
            print(f"❌ NOT DETECTED via 'which'")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False
    
    # Test 2: Direct command execution
    print(f"\nTrying direct execution...")
    try:
        result2 = subprocess.run(
            [tool_name, '--version'],
            capture_output=True,
            text=True,
            timeout=10,
            stderr=subprocess.STDOUT
        )
        print(f"Command: {tool_name} --version")
        print(f"Exit code: {result2.returncode}")
        if result2.returncode == 0:
            print(f"✅ Can execute {tool_name} directly")
        else:
            print(f"⚠️  Exit code non-zero but tool may still work")
    except FileNotFoundError:
        print(f"❌ FileNotFoundError: {tool_name} not found in PATH")
    except Exception as e:
        print(f"❌ ERROR: {e}")
    
    return False


def main():
    print("""
╔══════════════════════════════════════════════════════════╗
║      EMYUEL Tool Detection Diagnostic                   ║
║  Testing if Python can detect installed tools           ║
╚══════════════════════════════════════════════════════════╝
""")
    
    print(f"Python: {sys.version}")
    print(f"Executable: {sys.executable}")
    
    # Test the three required tools
    tools = ['sqlmap', 'nmap', 'nikto']
    
    results = {}
    for tool in tools:
        results[tool] = test_which(tool)
    
    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print('='*60)
    
    for tool, detected in results.items():
        status = "✅ DETECTED" if detected else "❌ NOT DETECTED"
        print(f"{tool:12} : {status}")
    
    print()
    
    detected_count = sum(1 for d in results.values() if d)
    total_count = len(results)
    
    if detected_count == total_count:
        print(f"✅ All {total_count} tools detected!")
        print("   → check_security_tools.py SHOULD work")
        return 0
    else:
        print(f"❌ Only {detected_count}/{total_count} tools detected")
        print("   → There's a problem with Python subprocess detection")
        return 1


if __name__ == "__main__":
    sys.exit(main())

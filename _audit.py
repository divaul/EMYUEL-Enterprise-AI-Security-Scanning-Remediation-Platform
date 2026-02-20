import sys
sys.path.insert(0, r'gui')
from security_tools import SECURITY_TOOLS

RECON_CATEGORIES = {
    'Network Scanner', 'Port Scanner', 'Subdomain',
    'Subdomain Takeover', 'OSINT/Recon', 'HTTP Probe',
    'DNS Recon', 'Web Recon', 'Web Crawler',
    'Visual Recon', 'Fingerprinting', 'URL Manipulation',
    'Pattern Grep', 'Param Discovery', 'Dir Discovery',
    'Dir Scanner', 'API Testing', 'SSL/TLS', 'Wordlists',
}

ALL_CATEGORIES = set()
RECON_TOOLS = []
VULN_TOOLS = []

for tid, info in SECURITY_TOOLS.items():
    cat = info.get('category', 'Unknown')
    ALL_CATEGORIES.add(cat)
    if cat in RECON_CATEGORIES:
        RECON_TOOLS.append((tid, cat))
    else:
        VULN_TOOLS.append((tid, cat))

print("=== ALL CATEGORIES ===")
for c in sorted(ALL_CATEGORIES):
    tag = "[RECON]" if c in RECON_CATEGORIES else "[VULN] "
    print(f"  {tag} {c}")

print("\n=== RECON PHASE tools ===")
for tid, cat in sorted(RECON_TOOLS):
    print(f"  {tid:<25} {cat}")

print("\n=== VULN PHASE tools ===")
for tid, cat in sorted(VULN_TOOLS):
    print(f"  {tid:<25} {cat}")

# Also check _build_cmd coverage
import importlib.util
spec = importlib.util.spec_from_file_location("tool_executor", r"gui/tool_executor.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

print("\n=== _build_cmd vs SECURITY_TOOLS mismatch ===")
in_tools_not_cmd = [tid for tid in SECURITY_TOOLS if not hasattr(mod, '_build_cmd')]
# Test actual build
ctx = {'wordlist': None, 'temp_dir': '/tmp'}
for tid in sorted(SECURITY_TOOLS.keys()):
    result = mod._build_cmd(tid, 'http://example.com', ctx)
    if result is None:
        print(f"  SKIP (no cmd): {tid}")

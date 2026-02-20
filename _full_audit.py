import sys; sys.path.insert(0, '.')
from gui.security_tools import SECURITY_TOOLS
from gui.tool_executor import _build_cmd, _resolve_cmd

recon_cats = {
    'Network Scanner','Port Scanner','Subdomain','Subdomain Takeover','OSINT/Recon',
    'HTTP Probe','DNS Recon','Web Recon','Web Crawler','Visual Recon','Fingerprinting',
    'URL Manipulation','Pattern Grep','Param Discovery','Dir Discovery','Dir Scanner',
    'API Testing','SSL/TLS','Wordlists',
}

cli_tools  = [(t,i) for t,i in SECURITY_TOOLS.items() if i.get('check_cmd')]
lib_tools  = [(t,i) for t,i in SECURITY_TOOLS.items() if not i.get('check_cmd')]
recon_cli  = [(t,i) for t,i in cli_tools if i.get('category') in recon_cats]
vuln_cli   = [(t,i) for t,i in cli_tools if i.get('category') not in recon_cats]

print("=== SECURITY_TOOLS REGISTRY ===")
print(f"Total entries      : {len(SECURITY_TOOLS)}")
print(f"CLI tools (binary) : {len(cli_tools)}")
print(f"  -> Recon phase   : {len(recon_cli)}")
print(f"  -> Vuln phase    : {len(vuln_cli)}")
print(f"Lib/SDK entries    : {len(lib_tools)}  (no check_cmd, harmlessly skipped by executor)")
print()
print("=== RECON CLI tools ===")
for t, i in sorted(recon_cli, key=lambda x: x[1]['category']):
    print(f"  [{i['category']:22}] {t:22} {i['name']}")
print()
print("=== VULN CLI tools ===")
for t, i in sorted(vuln_cli, key=lambda x: x[1]['category']):
    print(f"  [{i['category']:22}] {t:22} {i['name']}")
print()
print("=== LIB/SDK (no CLI) ===")
for t, i in lib_tools:
    print(f"  [{i['category']:22}] {t:22} {i['name']}")
print()

# --- _build_cmd coverage check ---
no_builder = []
for tid in SECURITY_TOOLS:
    try:
        _build_cmd(tid, 'https://example.com', {})
    except KeyError:
        no_builder.append(tid)
    except Exception:
        pass

print("=== _build_cmd coverage ===")
if no_builder:
    print(f"MISSING builders: {no_builder}")
else:
    print(f"OK: all {len(SECURITY_TOOLS)} tools handled in _build_cmd (no KeyError)")

# --- GUI integration check ---
with open('gui/emyuel_gui.py', 'r', encoding='utf-8') as f:
    src = f.read()

checks = [
    ('ToolExecutor(',               'ToolExecutor instantiated'),
    ('_run_external_tools',         'Quick/Advanced Scan: _run_external_tools'),
    ('quick_ext_tool_vars',         'Quick Scan: tool checkboxes'),
    ('adv_ext_tool_vars',           'Advanced Scan: tool checkboxes'),
    ('_run_ai_phase0_recon',        'AI Analysis: Phase 0 recon method'),
    ('recon_summary',               'AI Analysis: recon data injected into LLM prompt'),
    ('exec_type',                   'AI Analysis: Phase 4 exec_type schema'),
    ('_build_cmd, _resolve_cmd',    'AI Analysis: CLI imports for Phase 4'),
    ('badge_text',                  'AI Analysis: HTTP/CLI badges on step cards'),
    ('run_in_executor',             'AI Analysis: Phase 0 async executor'),
]

print()
print("=== GUI Integration Checks ===")
all_pass = True
for pat, desc in checks:
    found = pat in src
    status = "OK  " if found else "FAIL"
    if not found:
        all_pass = False
    print(f"  {status}: {desc}")

print()
if all_pass:
    print("ALL INTEGRATION CHECKS PASSED")
else:
    print("SOME INTEGRATION CHECKS FAILED - see above")

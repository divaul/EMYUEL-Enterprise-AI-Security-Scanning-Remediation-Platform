"""
tool_executor.py — External security tool execution engine for EMYUEL

Runs selected CLI security tools against scan targets via subprocess,
parses output into unified findings, and reports progress in real-time.
Supports pipeline chains: output from tool A feeds as stdin to tool B.
"""

import subprocess
import shutil
import os
import re
import pathlib
import tempfile
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse


# ─── Helpers ──────────────────────────────────────────────────────

def _extract_domain(target):
    """Extract domain/host from a URL or return as-is if already a domain."""
    if target.startswith(('http://', 'https://')):
        parsed = urlparse(target)
        return parsed.hostname or target
    return target


def _is_url(target):
    return target.startswith(('http://', 'https://'))


def _is_path(target):
    return os.path.exists(target)


def _find_wordlist():
    """Find a usable wordlist on the system."""
    candidates = [
        '/usr/share/seclists/Discovery/Web-Content/common.txt',
        '/usr/share/wordlists/dirb/common.txt',
        '/usr/share/wordlists/dirbuster/directory-list-2.3-small.txt',
        '/usr/share/seclists/Discovery/Web-Content/directory-list-2.3-small.txt',
    ]
    for wl in candidates:
        if os.path.isfile(wl):
            return wl
    # Check Windows paths
    home = pathlib.Path.home()
    win_candidates = [
        home / 'SecLists' / 'Discovery' / 'Web-Content' / 'common.txt',
        home / 'wordlists' / 'common.txt',
        pathlib.Path('C:/tools/SecLists/Discovery/Web-Content/common.txt'),
    ]
    for wl in win_candidates:
        if wl.is_file():
            return str(wl)
    return None


def _find_resolver_file():
    """Find a DNS resolver list."""
    candidates = [
        '/usr/share/seclists/Discovery/DNS/resolvers.txt',
        '/etc/resolv.conf',
    ]
    for r in candidates:
        if os.path.isfile(r):
            return r
    return None


# ─── Command Builders ────────────────────────────────────────────
# Returns (cmd_list, timeout_seconds, stdin_data_or_None) or None

def _build_cmd(tool_id, target, context=None):
    """
    Build the command for a tool.
    context: dict with optional keys like 'wordlist', 'temp_dir', 'subdomains_file'
    Returns: (cmd_list, timeout, stdin_data) or None
    """
    ctx = context or {}
    domain = _extract_domain(target)
    wordlist = ctx.get('wordlist') or _find_wordlist()
    temp_dir = ctx.get('temp_dir', tempfile.gettempdir())
    is_url_target = _is_url(target)
    is_path_target = _is_path(target)

    builders = {
        # ─── Network Scanners
        'nmap': lambda: (['nmap', '-sV', '-sC', '--top-ports', '100', '-T4', domain], 120, None),
        'masscan': lambda: (['masscan', domain, '-p1-1000', '--rate=1000'], 120, None),
        'rustscan': lambda: (['rustscan', '-a', domain, '--', '-sV'], 120, None),
        'naabu': lambda: (['naabu', '-host', domain, '-top-ports', '100'], 90, None),

        # ─── Web Scanners
        'nikto': lambda: (['nikto', '-h', target, '-maxtime', '120'], 150, None) if is_url_target else None,
        'wapiti': lambda: (['wapiti', '-u', target, '--flush-session', '-m', 'common', '--max-scan-time', '120'], 150, None) if is_url_target else None,
        'skipfish': lambda: (['skipfish', '-o', os.path.join(temp_dir, f'skipfish_{domain}'), '-W', '/dev/null', target], 180, None) if is_url_target else None,
        'whatweb': lambda: (['whatweb', '-v', target], 60, None) if is_url_target else None,

        # ─── SQL Injection
        'sqlmap': lambda: (['sqlmap', '-u', target, '--batch', '--level=1', '--risk=1', '--timeout=30', '--flush-session'], 180, None) if is_url_target else None,

        # ─── XSS
        'dalfox': lambda: (['dalfox', 'url', target, '--silence'], 120, None) if is_url_target else None,
        'xsstrike': lambda: (['xsstrike', '-u', target, '--skip'], 120, None) if is_url_target else None,

        # ─── SSTI / SSRF
        'tplmap': lambda: (['tplmap', '-u', target], 120, None) if is_url_target else None,
        'ssrfmap': lambda: (['ssrfmap', '-r', target, '-p', 'url', '--auto'], 120, None) if is_url_target and '=' in target else None,

        # ─── Dir Discovery
        'gobuster': lambda: (['gobuster', 'dir', '-u', target, '-w', wordlist, '-q', '-t', '20'], 120, None) if (is_url_target and wordlist) else None,
        'dirb': lambda: (['dirb', target, '-S', '-r'], 120, None) if is_url_target else None,
        'dirsearch': lambda: (['dirsearch', '-u', target, '--quiet', '-t', '20'], 120, None) if is_url_target else None,
        'feroxbuster': lambda: (['feroxbuster', '-u', target, '-q', '--time-limit', '120s'], 150, None) if is_url_target else None,

        # ─── Fuzzing
        'ffuf': lambda: (['ffuf', '-u', target.rstrip('/') + '/FUZZ', '-w', wordlist, '-mc', '200,301,302,403', '-t', '20'], 120, None) if (is_url_target and wordlist) else None,
        'wfuzz': lambda: (['wfuzz', '-c', '--hc', '404', '-w', wordlist, target.rstrip('/') + '/FUZZ'], 120, None) if (is_url_target and wordlist) else None,

        # ─── Brute Force (configured for HTTP form brute-force by default)
        'hydra': lambda: (['hydra', '-L', _default_users_file(), '-P', _default_pass_file(), '-f', '-V', '-t', '4', domain, 'http-get', '/'], 180, None) if (_default_users_file() and _default_pass_file()) else None,
        'medusa': lambda: (['medusa', '-h', domain, '-U', _default_users_file(), '-P', _default_pass_file(), '-M', 'http', '-n', '80', '-f'], 180, None) if (_default_users_file() and _default_pass_file()) else None,
        'john': lambda: None,     # Requires hash file — user must provide
        'hashcat': lambda: None,  # Requires hash file — user must provide

        # ─── CMS
        'wpscan': lambda: (['wpscan', '--url', target, '--enumerate', 'vp,vt,u', '--no-banner'], 180, None) if is_url_target else None,
        'droopescan': lambda: (['droopescan', 'scan', '-u', target], 120, None) if is_url_target else None,
        'joomscan': lambda: (['joomscan', '-u', target], 120, None) if is_url_target else None,

        # ─── Subdomain & Recon
        'subfinder': lambda: (['subfinder', '-d', domain, '-silent'], 90, None),
        'amass': lambda: (['amass', 'enum', '-d', domain, '-passive', '-timeout', '2'], 180, None),
        'findomain': lambda: (['findomain', '-t', domain, '-q'], 90, None),
        'chaos': lambda: (['chaos', '-d', domain, '-silent'], 60, None),
        'github_subdomains': lambda: (['github-subdomains', '-d', domain], 90, None),
        'subjack': lambda: _subjack_cmd(domain, ctx),
        'assetfinder': lambda: (['assetfinder', '--subs-only', domain], 60, None),

        # ─── HTTP Probing (stdin: one URL/domain per line)
        'httpx_tool': lambda: (['httpx', '-u', target, '-silent', '-status-code', '-title', '-tech-detect'], 60, None),
        'httprobe': lambda: (['httprobe'], 60, f"{domain}\n"),

        # ─── Vulnerability Scanning
        'nuclei': lambda: (['nuclei', '-u', target, '-severity', 'low,medium,high,critical', '-silent', '-nc'], 300, None) if is_url_target else None,
        'openvas': lambda: None,  # Requires full GVM setup — cannot auto-configure
        'interactsh_client': lambda: (['interactsh-client', '-n', '1', '-v'], 30, None),

        # ─── SSL/TLS
        'sslscan': lambda: (['sslscan', '--no-colour', domain], 60, None),
        'sslyze': lambda: (['sslyze', domain], 90, None),
        'testssl': lambda: (['testssl', '--quiet', '--color', '0', domain], 120, None),

        # ─── Command Injection
        'commix': lambda: (['commix', '-u', target, '--batch', '--level=1'], 120, None) if is_url_target else None,

        # ─── Param Discovery / URL Manipulation
        'paramspider': lambda: (['paramspider', '-d', domain], 90, None),
        'arjun': lambda: (['arjun', '-u', target, '-q'], 120, None) if is_url_target else None,
        'qsreplace': lambda: (['qsreplace', 'FUZZ'], 30, f"{target}?id=1\n{target}?page=test\n{target}?q=hello\n") if is_url_target else None,
        'unfurl': lambda: (['unfurl', 'domains'], 30, f"{target}\n"),
        'gf': lambda: (['gf', 'xss'], 30, f"{target}?id=1\n{target}?page=test\n{target}?redirect=http://evil.com\n") if is_url_target else None,

        # ─── Web Proxy (ZAP can run automated scan via CLI)
        'burpsuite': lambda: None,   # GUI only
        'owasp_zap': lambda: (['zap-cli', 'quick-scan', '-s', 'xss,sqli', '-r', target], 300, None) if is_url_target else None,
        'mitmproxy': lambda: None,   # Interactive only

        # ─── API Testing
        'newman': lambda: None,      # Requires Postman collection file
        'kiterunner': lambda: (['kr', 'brute', target, '-w', wordlist], 120, None) if (is_url_target and wordlist) else None,

        # ─── Web Recon / URL Collection
        'waybackurls': lambda: (['waybackurls', domain], 60, None),
        'gau': lambda: (['gau', domain], 60, None),
        'hakrawler': lambda: (['hakrawler', '-d', '2'], 90, f"{target}\n") if is_url_target else None,
        'katana': lambda: (['katana', '-u', target, '-silent', '-d', '2'], 120, None) if is_url_target else None,

        # ─── Visual Recon
        'aquatone': lambda: (['aquatone', '-out', os.path.join(temp_dir, f'aquatone_{domain}')], 120, f"{target}\n") if is_url_target else None,
        'gowitness': lambda: (['gowitness', 'single', target], 60, None) if is_url_target else None,

        # ─── DNS Recon
        'dnsx': lambda: (['dnsx', '-d', domain, '-silent'], 60, None),
        'shuffledns': lambda: _shuffledns_cmd(domain, wordlist),

        # ─── SAST (for local paths)
        'semgrep': lambda: (['semgrep', 'scan', '--config=auto', '--quiet', target], 180, None) if is_path_target else None,
        'bandit': lambda: (['bandit', '-r', target, '-q', '-f', 'screen'], 120, None) if is_path_target else None,
        'brakeman': lambda: (['brakeman', '-q', '-p', target], 120, None) if is_path_target else None,

        # ─── Secret Scanning (for local paths)
        'gitleaks': lambda: (['gitleaks', 'detect', '--source', target, '--no-banner'], 120, None) if is_path_target else None,
        'trufflehog': lambda: (['trufflehog', 'filesystem', target, '--no-update'], 120, None) if is_path_target else None,
        'detect_secrets': lambda: (['detect-secrets', 'scan', target], 90, None) if is_path_target else None,

        # ─── Wordlists (not executable, resource only)
        'seclists': lambda: None,

        # ─── Exploitation
        'searchsploit': lambda: (['searchsploit', domain], 30, None),

        # ─── Python libraries / AI SDKs (not CLI tools)
        'aiohttp': lambda: None,
        'httpx_pkg': lambda: None,
        'requests': lambda: None,
        'beautifulsoup': lambda: None,
        'scrapy': lambda: None,
        'google_genai': lambda: None,
        'openai_sdk': lambda: None,
        'anthropic_sdk': lambda: None,

        # ─── Reporting (not scan tools)
        'dradis': lambda: None,
        'faraday': lambda: None,
        'defectdojo': lambda: None,
    }

    builder = builders.get(tool_id)
    if not builder:
        return None
    try:
        return builder()
    except Exception:
        return None


# ─── Special command builders for tools needing file setup ─────────

def _default_users_file():
    """Find a default usernames wordlist."""
    candidates = [
        '/usr/share/seclists/Usernames/top-usernames-shortlist.txt',
        '/usr/share/wordlists/metasploit/http_default_users.txt',
    ]
    for f in candidates:
        if os.path.isfile(f):
            return f
    return None


def _default_pass_file():
    """Find a default passwords wordlist."""
    candidates = [
        '/usr/share/seclists/Passwords/Common-Credentials/top-20-common-SSH-passwords.txt',
        '/usr/share/wordlists/metasploit/http_default_pass.txt',
        '/usr/share/wordlists/rockyou.txt',
    ]
    for f in candidates:
        if os.path.isfile(f):
            return f
    return None


def _subjack_cmd(domain, ctx):
    """Build subjack command — auto-generates subdomain list if available."""
    subs_file = ctx.get('subdomains_file')
    if subs_file and os.path.isfile(subs_file):
        return (['subjack', '-w', subs_file, '-t', '20', '-v', '-ssl', '-a'], 120, None)
    # Can also take domain directly with a single-entry temp file
    tmp = os.path.join(tempfile.gettempdir(), f'subjack_{domain}.txt')
    try:
        with open(tmp, 'w') as f:
            f.write(domain + '\n')
        return (['subjack', '-w', tmp, '-t', '20', '-v', '-ssl', '-a'], 120, None)
    except Exception:
        return None


def _shuffledns_cmd(domain, wordlist):
    """Build shuffledns command with wordlist and resolver."""
    resolver = _find_resolver_file()
    if not wordlist or not resolver:
        return None
    return (['shuffledns', '-d', domain, '-w', wordlist, '-r', resolver, '-silent'], 120, None)


# ─── Pipeline Chains ─────────────────────────────────────────────
# Pipelines run tool A, capture output, feed as stdin to tool B.
# These run automatically if BOTH tools are selected.

PIPELINE_CHAINS = [
    # (source_tool, dest_tool, description)
    # subfinder → httprobe: find subdomains then probe which are alive
    ('subfinder', 'httprobe', 'Probing discovered subdomains'),
    # waybackurls → gf: find archived URLs then grep for patterns
    ('waybackurls', 'gf', 'Filtering archived URLs for vuln patterns'),
    # gau → qsreplace: get all URLs then replace query params
    ('gau', 'qsreplace', 'Replacing query params for fuzzing'),
    # subfinder → aquatone: find subdomains then screenshot them
    ('subfinder', 'aquatone', 'Screenshotting discovered subdomains'),
    # katana → unfurl: crawl site then extract URL components
    ('katana', 'unfurl', 'Extracting URL components from crawled pages'),
    # hakrawler → dalfox: crawl for URLs then test for XSS
    ('hakrawler', 'dalfox', 'Testing crawled URLs for XSS'),
]


# ─── Path resolution ─────────────────────────────────────────────

def _find_cmd_in_extra_paths(cmd_name):
    """Search for a command in common extra paths (GOPATH, cargo, etc.)"""
    home = pathlib.Path.home()
    extra_dirs = [
        home / 'go' / 'bin',
        home / '.local' / 'bin',
        home / '.cargo' / 'bin',
        pathlib.Path('/usr/local/go/bin'),
        pathlib.Path('/usr/local/bin'),
        pathlib.Path('/snap/bin'),
    ]
    gopath = os.environ.get('GOPATH', '')
    if gopath:
        extra_dirs.append(pathlib.Path(gopath) / 'bin')
    gobin = os.environ.get('GOBIN', '')
    if gobin:
        extra_dirs.append(pathlib.Path(gobin))

    for d in extra_dirs:
        try:
            if not d.is_dir():
                continue
        except (OSError, ValueError):
            continue
        candidate = d / cmd_name
        if candidate.is_file():
            return str(candidate)
        candidate_exe = d / f"{cmd_name}.exe"
        if candidate_exe.is_file():
            return str(candidate_exe)
    return None


def _resolve_cmd(cmd_name):
    """Find the full path for a command, checking PATH + extra dirs."""
    return shutil.which(cmd_name) or _find_cmd_in_extra_paths(cmd_name)


# ─── Output Parsers ──────────────────────────────────────────────

def _parse_output_to_findings(tool_id, tool_name, output_text, target):
    """Convert raw tool output into structured findings list."""
    findings = []

    if not output_text or not output_text.strip():
        return findings

    lines = output_text.strip().split('\n')

    # Nuclei: [severity] [template-id] [protocol] target
    if tool_id == 'nuclei':
        for line in lines:
            line = line.strip()
            if not line:
                continue
            severity = 'info'
            for sev in ['critical', 'high', 'medium', 'low']:
                if f'[{sev}]' in line.lower():
                    severity = sev
                    break
            findings.append({
                'title': f'[Nuclei] {line[:120]}',
                'severity': severity,
                'description': line,
                'source': f'external:{tool_name}',
                'tool': tool_name,
                'target': target,
            })
        return findings

    # Nmap — open ports
    if tool_id == 'nmap':
        for line in lines:
            if '/tcp' in line or '/udp' in line:
                parts = line.split()
                if len(parts) >= 3 and 'open' in parts[1]:
                    findings.append({
                        'title': f'[Nmap] Open port: {parts[0]} ({parts[2]})',
                        'severity': 'info',
                        'description': line.strip(),
                        'source': f'external:{tool_name}',
                        'tool': tool_name,
                        'target': target,
                    })
        return findings

    # Subdomain tools — each line is a subdomain
    if tool_id in ('subfinder', 'amass', 'findomain', 'chaos', 'github_subdomains', 'assetfinder'):
        unique_subs = set()
        for line in lines:
            sub = line.strip()
            if sub and '.' in sub and sub not in unique_subs:
                unique_subs.add(sub)
        if unique_subs:
            findings.append({
                'title': f'[{tool_name}] Found {len(unique_subs)} subdomains',
                'severity': 'info',
                'description': '\n'.join(sorted(unique_subs)[:50]),
                'source': f'external:{tool_name}',
                'tool': tool_name,
                'target': target,
            })
        return findings

    # URL collectors — each line is a URL
    if tool_id in ('waybackurls', 'gau', 'katana', 'hakrawler'):
        urls = [l.strip() for l in lines if l.strip().startswith('http')]
        if urls:
            findings.append({
                'title': f'[{tool_name}] Discovered {len(urls)} URLs',
                'severity': 'info',
                'description': '\n'.join(urls[:30]) + (f'\n... and {len(urls)-30} more' if len(urls) > 30 else ''),
                'source': f'external:{tool_name}',
                'tool': tool_name,
                'target': target,
            })
        return findings

    # httprobe — alive hosts
    if tool_id == 'httprobe':
        alive = [l.strip() for l in lines if l.strip().startswith('http')]
        if alive:
            findings.append({
                'title': f'[httprobe] {len(alive)} live hosts',
                'severity': 'info',
                'description': '\n'.join(alive[:30]),
                'source': f'external:{tool_name}',
                'tool': tool_name,
                'target': target,
            })
        return findings

    # subjack — takeover vulns
    if tool_id == 'subjack':
        for line in lines:
            if 'vulnerable' in line.lower() or 'takeover' in line.lower():
                findings.append({
                    'title': f'[Subjack] Subdomain takeover possible',
                    'severity': 'high',
                    'description': line.strip(),
                    'source': f'external:{tool_name}',
                    'tool': tool_name,
                    'target': target,
                })
        return findings

    # SQLMap — injection confirmations
    if tool_id == 'sqlmap':
        for line in lines:
            if 'is vulnerable' in line.lower() or 'injectable' in line.lower():
                findings.append({
                    'title': f'[SQLMap] SQL Injection found',
                    'severity': 'critical',
                    'description': line.strip(),
                    'source': f'external:{tool_name}',
                    'tool': tool_name,
                    'target': target,
                })
        return findings

    # Dalfox — XSS
    if tool_id == 'dalfox':
        for line in lines:
            if 'vuln' in line.lower() or 'xss' in line.lower() or 'POC' in line:
                findings.append({
                    'title': f'[Dalfox] XSS vulnerability',
                    'severity': 'high',
                    'description': line.strip(),
                    'source': f'external:{tool_name}',
                    'tool': tool_name,
                    'target': target,
                })
        return findings

    # Bandit — Python security
    if tool_id == 'bandit':
        for line in lines:
            for sev in ['HIGH', 'MEDIUM', 'LOW']:
                if f'Severity: {sev}' in line:
                    findings.append({
                        'title': f'[Bandit] {line.strip()[:100]}',
                        'severity': sev.lower(),
                        'description': line.strip(),
                        'source': f'external:{tool_name}',
                        'tool': tool_name,
                        'target': target,
                    })
        return findings

    # Gitleaks — secrets
    if tool_id == 'gitleaks':
        for line in lines:
            if 'secret' in line.lower() or 'leak' in line.lower() or 'key' in line.lower():
                findings.append({
                    'title': f'[Gitleaks] Secret detected',
                    'severity': 'high',
                    'description': line.strip()[:200],
                    'source': f'external:{tool_name}',
                    'tool': tool_name,
                    'target': target,
                })
        return findings

    # Hydra / Medusa — cracked creds
    if tool_id in ('hydra', 'medusa'):
        for line in lines:
            if 'login:' in line.lower() or 'password:' in line.lower() or 'success' in line.lower():
                findings.append({
                    'title': f'[{tool_name}] Credential found',
                    'severity': 'critical',
                    'description': line.strip()[:200],
                    'source': f'external:{tool_name}',
                    'tool': tool_name,
                    'target': target,
                })
        return findings

    # SSLScan/SSLyze — weak ciphers / expired certs
    if tool_id in ('sslscan', 'sslyze', 'testssl'):
        for line in lines:
            ll = line.lower()
            if any(kw in ll for kw in ['expired', 'weak', 'vulnerable', 'rejected', 'insecure', 'sslv', 'tlsv1.0']):
                findings.append({
                    'title': f'[{tool_name}] SSL/TLS issue',
                    'severity': 'medium',
                    'description': line.strip()[:200],
                    'source': f'external:{tool_name}',
                    'tool': tool_name,
                    'target': target,
                })
        if not findings:
            # No issues found, report clean
            findings.append({
                'title': f'[{tool_name}] SSL/TLS scan complete',
                'severity': 'info',
                'description': f'No major issues found. {len(lines)} lines analyzed.',
                'source': f'external:{tool_name}',
                'tool': tool_name,
                'target': target,
            })
        return findings

    # WPScan — WordPress vulns
    if tool_id == 'wpscan':
        for line in lines:
            if 'vulnerability' in line.lower() or 'vuln' in line.lower():
                findings.append({
                    'title': f'[WPScan] WordPress vulnerability',
                    'severity': 'high',
                    'description': line.strip()[:200],
                    'source': f'external:{tool_name}',
                    'tool': tool_name,
                    'target': target,
                })
        return findings

    # Commix — command injection
    if tool_id == 'commix':
        for line in lines:
            if 'vulnerable' in line.lower() or 'injection' in line.lower():
                findings.append({
                    'title': f'[Commix] Command injection found',
                    'severity': 'critical',
                    'description': line.strip()[:200],
                    'source': f'external:{tool_name}',
                    'tool': tool_name,
                    'target': target,
                })
        return findings

    # Generic — report full output
    truncated = output_text[:2000]
    if len(output_text) > 2000:
        truncated += f'\n... ({len(output_text)} bytes total)'
    findings.append({
        'title': f'[{tool_name}] Scan results',
        'severity': 'info',
        'description': truncated,
        'source': f'external:{tool_name}',
        'tool': tool_name,
        'target': target,
    })
    return findings


# ─── Tool Executor Class ─────────────────────────────────────────

class ToolExecutor:
    """
    Executes external security tools against a target.
    Supports: direct commands, stdin piping, and pipeline chains.

    Usage:
        executor = ToolExecutor(target, selected_tools, tool_registry, log_fn)
        findings = executor.run_all()
    """

    def __init__(self, target, selected_tool_ids, tool_registry, log_fn=None, max_workers=5):
        self.target = target
        self.selected_tool_ids = set(selected_tool_ids)
        self.tool_registry = tool_registry
        self.log = log_fn or (lambda msg: None)
        self.max_workers = max_workers
        self.all_findings = []
        self._tool_outputs = {}           # tool_id → stdout text (for pipeline chains)
        self._context = {                 # shared context available to all builders
            'temp_dir': tempfile.mkdtemp(prefix='emyuel_'),
            'wordlist': _find_wordlist(),
        }

    def run_all(self):
        """Run all selected tools concurrently, then run pipeline chains."""
        runnable = []
        skipped_not_installed = []
        skipped_not_applicable = []

        for tool_id in self.selected_tool_ids:
            info = self.tool_registry.get(tool_id)
            if not info:
                continue

            # Build command
            result = _build_cmd(tool_id, self.target, self._context)

            if result is None:
                skipped_not_applicable.append(info['name'])
                continue

            cmd_list, timeout, stdin_data = result

            # Check if tool is installed
            cmd_exe = cmd_list[0]
            resolved = _resolve_cmd(cmd_exe)
            if not resolved:
                skipped_not_installed.append(info['name'])
                continue

            cmd_list[0] = resolved
            runnable.append((tool_id, info, cmd_list, timeout, stdin_data))

        # Log summary
        ts = datetime.now().strftime('%H:%M:%S')
        total_selected = len(self.selected_tool_ids)
        self.log(f"\n[{ts}] 🔧 External Tools: {len(runnable)} runnable / {total_selected} selected")

        if skipped_not_installed:
            self.log(f"  ⚠️ Not installed: {', '.join(skipped_not_installed[:10])}"
                     + (f' +{len(skipped_not_installed)-10} more' if len(skipped_not_installed) > 10 else ''))

        if skipped_not_applicable:
            self.log(f"  ℹ️ Not applicable: {', '.join(skipped_not_applicable[:8])}"
                     + (f' +{len(skipped_not_applicable)-8} more' if len(skipped_not_applicable) > 8 else ''))

        if not runnable:
            self.log(f"[{ts}] ℹ️ No external tools to run.")
            return []

        # Run all tools concurrently
        tool_names = ', '.join(info['name'] for _, info, _, _, _ in runnable)
        self.log(f"[{ts}] 🚀 Running: {tool_names}")

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(self._run_single, tool_id, info, cmd_list, timeout, stdin_data): tool_id
                for tool_id, info, cmd_list, timeout, stdin_data in runnable
            }
            for future in as_completed(futures):
                tool_id = futures[future]
                try:
                    findings = future.result(timeout=600)
                    self.all_findings.extend(findings)
                except Exception as e:
                    self.log(f"  ❌ {tool_id}: unhandled error: {e}")

        # Run pipeline chains (if both source and dest were selected)
        self._run_pipelines()

        ts = datetime.now().strftime('%H:%M:%S')
        self.log(f"[{ts}] ✅ External tools complete: {len(self.all_findings)} findings total")
        return self.all_findings

    def _run_single(self, tool_id, info, cmd_list, timeout, stdin_data=None):
        """Run a single tool and return findings."""
        tool_name = info['name']
        ts = datetime.now().strftime('%H:%M:%S')
        self.log(f"  [{ts}] ▶ {tool_name}...")

        try:
            result = subprocess.run(
                cmd_list,
                capture_output=True,
                text=True,
                timeout=timeout,
                input=stdin_data,
                env={**os.environ, 'TERM': 'dumb', 'NO_COLOR': '1'},
            )
            output = (result.stdout or '') + (result.stderr or '')
            exit_code = result.returncode

            # Store stdout for pipeline chains
            if result.stdout and result.stdout.strip():
                self._tool_outputs[tool_id] = result.stdout.strip()

            ts2 = datetime.now().strftime('%H:%M:%S')

            if exit_code == 0 or output.strip():
                line_count = len(output.strip().split('\n')) if output.strip() else 0
                self.log(f"  [{ts2}] ✅ {tool_name} — {line_count} lines output")
                return _parse_output_to_findings(tool_id, tool_name, output.strip(), self.target)
            else:
                self.log(f"  [{ts2}] ⚠️ {tool_name} — exit code {exit_code}, no output")
                return []

        except subprocess.TimeoutExpired:
            ts2 = datetime.now().strftime('%H:%M:%S')
            self.log(f"  [{ts2}] ⏰ {tool_name} — timed out after {timeout}s")
            return [{
                'title': f'[{tool_name}] Scan timed out',
                'severity': 'info',
                'description': f'{tool_name} timed out after {timeout} seconds',
                'source': f'external:{tool_name}',
                'tool': tool_name,
                'target': self.target,
            }]
        except Exception as e:
            ts2 = datetime.now().strftime('%H:%M:%S')
            self.log(f"  [{ts2}] ❌ {tool_name} — error: {e}")
            return []

    def _run_pipelines(self):
        """Run pipeline chains where source tool output feeds dest tool stdin."""
        for src_id, dst_id, desc in PIPELINE_CHAINS:
            # Only run if both tools were selected AND source produced output
            if src_id not in self.selected_tool_ids or dst_id not in self.selected_tool_ids:
                continue
            if src_id not in self._tool_outputs:
                continue

            src_output = self._tool_outputs[src_id]
            if not src_output.strip():
                continue

            # Build dest command with source output as stdin
            result = _build_cmd(dst_id, self.target, self._context)
            if result is None:
                continue

            cmd_list, timeout, _ = result
            cmd_exe = cmd_list[0]
            resolved = _resolve_cmd(cmd_exe)
            if not resolved:
                continue

            cmd_list[0] = resolved
            src_name = self.tool_registry.get(src_id, {}).get('name', src_id)
            dst_name = self.tool_registry.get(dst_id, {}).get('name', dst_id)
            dst_info = self.tool_registry.get(dst_id, {'name': dst_id})

            ts = datetime.now().strftime('%H:%M:%S')
            self.log(f"  [{ts}] 🔗 Pipeline: {src_name} → {dst_name} ({desc})")

            try:
                proc = subprocess.run(
                    cmd_list,
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    input=src_output,
                    env={**os.environ, 'TERM': 'dumb', 'NO_COLOR': '1'},
                )
                output = (proc.stdout or '') + (proc.stderr or '')
                if output.strip():
                    pipe_findings = _parse_output_to_findings(
                        f'{src_id}_to_{dst_id}', f'{src_name}→{dst_name}',
                        output.strip(), self.target
                    )
                    self.all_findings.extend(pipe_findings)
                    ts2 = datetime.now().strftime('%H:%M:%S')
                    self.log(f"  [{ts2}] ✅ Pipeline {src_name}→{dst_name}: {len(pipe_findings)} findings")
            except subprocess.TimeoutExpired:
                ts2 = datetime.now().strftime('%H:%M:%S')
                self.log(f"  [{ts2}] ⏰ Pipeline {src_name}→{dst_name} timed out")
            except Exception as e:
                ts2 = datetime.now().strftime('%H:%M:%S')
                self.log(f"  [{ts2}] ❌ Pipeline {src_name}→{dst_name}: {e}")

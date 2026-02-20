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
        'nmap': lambda: (['nmap', '-sV', '-sC', '--top-ports', '1000', '-T4', '--open', domain], 300, None),
        'masscan': lambda: (['masscan', domain, '-p1-65535', '--rate=1000'], 300, None),
        'rustscan': lambda: (['rustscan', '-a', domain, '--', '-sV', '-sC'], 300, None),
        'naabu': lambda: (['naabu', '-host', domain, '-top-ports', '1000'], 180, None),

        # ─── Web Scanners
        'nikto': lambda: (['nikto', '-h', target, '-maxtime', '300', '-Tuning', 'x'], 360, None) if is_url_target else None,
        'wapiti': lambda: (['wapiti', '-u', target, '--flush-session', '-m', 'common', '--max-scan-time', '300', '-d', '3'], 360, None) if is_url_target else None,
        'skipfish': lambda: (['skipfish', '-o', os.path.join(temp_dir, f'skipfish_{domain}'), '-W', '/dev/null', target], 300, None) if is_url_target else None,
        'whatweb': lambda: (['whatweb', '-v', '-a', '3', target], 90, None) if is_url_target else None,

        # ─── SQL Injection
        'sqlmap': lambda: (['sqlmap', '-u', target, '--batch', '--level=3', '--risk=2', '--timeout=60', '--flush-session', '--threads=3', '--crawl=2'], 420, None) if is_url_target else None,

        # ─── XSS
        'dalfox': lambda: (['dalfox', 'url', target, '--silence', '--deep-domxss'], 300, None) if is_url_target else None,
        'xsstrike': lambda: (['xsstrike', '-u', target, '--crawl', '-l', '3'], 300, None) if is_url_target else None,

        # ─── SSTI / SSRF
        'tplmap': lambda: (['tplmap', '-u', target, '--level', '5'], 300, None) if is_url_target else None,
        'ssrfmap': lambda: (['ssrfmap', '-r', target, '-p', 'url', '--auto'], 300, None) if is_url_target and '=' in target else None,

        # ─── Dir Discovery
        'gobuster': lambda: (['gobuster', 'dir', '-u', target, '-w', wordlist, '-q', '-t', '30', '--timeout', '10s'], 300, None) if (is_url_target and wordlist) else None,
        'dirb': lambda: (['dirb', target, '-S', '-r', '-z', '50'], 300, None) if is_url_target else None,
        'dirsearch': lambda: (['dirsearch', '-u', target, '--quiet', '-t', '30', '-r', '-R', '3'], 300, None) if is_url_target else None,
        'feroxbuster': lambda: (['feroxbuster', '-u', target, '-q', '--time-limit', '300s', '-d', '3', '-t', '30'], 360, None) if is_url_target else None,

        # ─── Fuzzing
        'ffuf': lambda: (['ffuf', '-u', target.rstrip('/') + '/FUZZ', '-w', wordlist, '-mc', '200,201,301,302,307,401,403,405,500', '-t', '30', '-recursion', '-recursion-depth', '2'], 300, None) if (is_url_target and wordlist) else None,
        'wfuzz': lambda: (['wfuzz', '-c', '--hc', '404', '-t', '30', '-w', wordlist, target.rstrip('/') + '/FUZZ'], 300, None) if (is_url_target and wordlist) else None,

        # ─── Brute Force (configured for HTTP form brute-force by default)
        'hydra': lambda: (['hydra', '-L', _default_users_file(), '-P', _default_pass_file(), '-f', '-V', '-t', '8', domain, 'http-get', '/'], 360, None) if (_default_users_file() and _default_pass_file()) else None,
        'medusa': lambda: (['medusa', '-h', domain, '-U', _default_users_file(), '-P', _default_pass_file(), '-M', 'http', '-n', '80', '-f', '-t', '8'], 360, None) if (_default_users_file() and _default_pass_file()) else None,
        'john': lambda: None,     # Requires hash file — user must provide
        'hashcat': lambda: None,  # Requires hash file — user must provide

        # ─── CMS
        'wpscan': lambda: (['wpscan', '--url', target, '--enumerate', 'vp,vt,u,cb,dbe', '--no-banner', '--detection-mode', 'aggressive'], 360, None) if is_url_target else None,
        'droopescan': lambda: (['droopescan', 'scan', '-u', target], 240, None) if is_url_target else None,
        'joomscan': lambda: (['joomscan', '-u', target, '-ec'], 240, None) if is_url_target else None,

        # ─── Subdomain & Recon
        'subfinder': lambda: (['subfinder', '-d', domain, '-silent', '-all'], 180, None),
        'amass': lambda: (['amass', 'enum', '-d', domain, '-passive', '-timeout', '10'], 600, None),
        'findomain': lambda: (['findomain', '-t', domain, '-q'], 180, None),
        'chaos': lambda: (['chaos', '-d', domain, '-silent'], 120, None),
        'github_subdomains': lambda: (['github-subdomains', '-d', domain], 180, None),
        'subjack': lambda: _subjack_cmd(domain, ctx),
        'assetfinder': lambda: (['assetfinder', '--subs-only', domain], 120, None),

        # ─── HTTP Probing (stdin: one URL/domain per line)
        'httpx_tool': lambda: (['httpx', '-u', target, '-silent', '-status-code', '-title', '-tech-detect', '-follow-redirects'], 120, None),
        'httprobe': lambda: (['httprobe'], 120, f"{domain}\n"),

        # ─── Vulnerability Scanning
        'nuclei': lambda: (['nuclei', '-u', target, '-severity', 'low,medium,high,critical', '-silent', '-nc', '-rl', '50', '-c', '10'], 600, None) if is_url_target else None,
        'openvas': lambda: None,  # Requires full GVM setup — cannot auto-configure
        'interactsh_client': lambda: (['interactsh-client', '-n', '1', '-v'], 60, None),

        # ─── SSL/TLS
        'sslscan': lambda: (['sslscan', '--no-colour', '--show-certificate', '--show-ciphers', domain], 120, None),
        'sslyze': lambda: (['sslyze', '--regular', domain], 180, None),
        'testssl': lambda: (['testssl', '--quiet', '--color', '0', '--full', domain], 300, None),

        # ─── Command Injection
        'commix': lambda: (['commix', '-u', target, '--batch', '--level=3', '--crawl=2'], 360, None) if is_url_target else None,

        # ─── Param Discovery / URL Manipulation
        'paramspider': lambda: (['paramspider', '-d', domain], 180, None),
        'arjun': lambda: (['arjun', '-u', target, '-q', '-t', '15'], 300, None) if is_url_target else None,
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
        'waybackurls': lambda: (['waybackurls', domain], 180, None),
        'gau': lambda: (['gau', '--threads', '5', domain], 180, None),
        'hakrawler': lambda: (['hakrawler', '-d', '4', '-t', '10'], 240, f"{target}\n") if is_url_target else None,
        'katana': lambda: (['katana', '-u', target, '-silent', '-d', '4', '-jc', '-kf'], 300, None) if is_url_target else None,

        # ─── Visual Recon
        'aquatone': lambda: (['aquatone', '-out', os.path.join(temp_dir, f'aquatone_{domain}')], 180, f"{target}\n") if is_url_target else None,
        'gowitness': lambda: (['gowitness', 'single', target], 120, None) if is_url_target else None,

        # ─── DNS Recon
        'dnsx': lambda: (['dnsx', '-d', domain, '-silent'], 60, None),
        'shuffledns': lambda: _shuffledns_cmd(domain, wordlist),

        # ─── SAST (for local paths)
        'semgrep': lambda: (['semgrep', 'scan', '--config=auto', '--quiet', target], 300, None) if is_path_target else None,
        'bandit': lambda: (['bandit', '-r', target, '-q', '-f', 'screen', '-ll'], 240, None) if is_path_target else None,
        'brakeman': lambda: (['brakeman', '-q', '-p', target], 240, None) if is_path_target else None,

        # ─── Secret Scanning (for local paths)
        'gitleaks': lambda: (['gitleaks', 'detect', '--source', target, '--no-banner', '-v'], 240, None) if is_path_target else None,
        'trufflehog': lambda: (['trufflehog', 'filesystem', target, '--no-update'], 240, None) if is_path_target else None,
        'detect_secrets': lambda: (['detect-secrets', 'scan', target], 180, None) if is_path_target else None,

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

        # ─── Metadata Analysis ──────────────────────────────────
        # For URL targets: we download all <img> tags and scan them
        # For path targets: recursive exiftool scan on local directory
        'exiftool': lambda: _exiftool_cmd(target, domain, temp_dir, is_url_target, is_path_target),
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
    lines = [l for l in output_text.strip().split('\n') if l.strip()]

    def _f(title, severity, description, **extra):
        return {
            'title': title, 'severity': severity, 'description': description,
            'source': f'external:{tool_name}', 'tool': tool_name, 'target': target,
            **extra,
        }

    # ── Nuclei ──────────────────────────────────────────────────────────
    if tool_id == 'nuclei':
        for line in lines:
            sev = next((s for s in ['critical','high','medium','low'] if f'[{s}]' in line.lower()), 'info')
            findings.append(_f(f'[Nuclei] {line[:120]}', sev, line))
        return findings

    # ── Nmap ────────────────────────────────────────────────────────────
    if tool_id == 'nmap':
        import re as _re
        HIGH_PORTS = {'21','23','3389','5900','69','161','512','513','514'}
        for line in lines:
            m = _re.match(r'(\d+)/(tcp|udp)\s+(open\S*)\s+(\S+)(.*)', line)
            if not m:
                continue
            port, proto, state, svc = m.group(1), m.group(2), m.group(3), m.group(4)
            high_svcs = {'ftp','telnet','rdp','vnc','rsh','rlogin','tftp','snmp'}
            sev = ('high' if (svc.lower() in high_svcs or port in HIGH_PORTS) else
                   'medium' if svc.lower() in {'http','https','ssh','smtp'} else 'info')
            findings.append(_f(f'[Nmap] Open {port}/{proto} — {svc}', sev, line.strip(),
                               port=port, protocol=proto, service=svc))
        return findings

    # ── Masscan ─────────────────────────────────────────────────────────
    if tool_id == 'masscan':
        import re as _re
        for line in lines:
            m = _re.search(r'port (\d+)/(\w+)\s+open', line)
            if m:
                findings.append(_f(f'[Masscan] Open port {m.group(1)}/{m.group(2)}', 'info', line.strip(), port=m.group(1)))
        return findings

    # ── Naabu ───────────────────────────────────────────────────────────
    if tool_id == 'naabu':
        for line in lines:
            if ':' in line:
                findings.append(_f(f'[Naabu] Open port: {line.strip()[:80]}', 'info', line.strip()))
        return findings

    # ── Nikto ───────────────────────────────────────────────────────────
    if tool_id == 'nikto':
        for line in lines:
            if not line.strip().startswith('+'):
                continue
            c = line.lstrip('+ ').strip()
            sev = ('high' if any(k in c.lower() for k in ['osvdb','xss','injection','allow']) else
                   'low' if any(k in c.lower() for k in ['server:','retrieved','cookie','info']) else 'medium')
            findings.append(_f(f'[Nikto] {c[:120]}', sev, c))
        return findings

    # ── WhatWeb ─────────────────────────────────────────────────────────
    if tool_id == 'whatweb':
        for line in lines:
            if line.strip() and not line.startswith('#'):
                findings.append(_f(f'[WhatWeb] {line.strip()[:120]}', 'info', line.strip()))
        return findings

    # ── httpx ───────────────────────────────────────────────────────────
    if tool_id == 'httpx_tool':
        for line in lines:
            sev = 'low' if any(c in line for c in ['[401]','[403]','[500]']) else 'info'
            findings.append(_f(f'[httpx] {line.strip()[:120]}', sev, line.strip()))
        return findings

    # ── Subdomain tools — each subdomain = 1 finding ────────────────────
    if tool_id in ('subfinder','amass','findomain','chaos','github_subdomains','assetfinder'):
        seen = set()
        for line in lines:
            sub = line.strip().lower()
            if sub and '.' in sub and sub not in seen:
                seen.add(sub)
                findings.append(_f(f'[{tool_name}] Subdomain: {sub}', 'info', sub, subdomain=sub))
        return findings

    # ── httprobe ────────────────────────────────────────────────────────
    if tool_id == 'httprobe':
        for line in lines:
            if line.strip().startswith('http'):
                findings.append(_f(f'[httprobe] Alive: {line.strip()[:100]}', 'info', line.strip(), url=line.strip()))
        return findings

    # ── URL collectors — each URL = 1 finding ───────────────────────────
    if tool_id in ('waybackurls','gau','katana','hakrawler'):
        for line in lines:
            line = line.strip()
            if not line.startswith('http'):
                continue
            sev = 'info'
            if '?' in line and '=' in line:
                sev = 'medium' if any(k in line.lower() for k in ['admin','config','debug','token','key','password','backup']) else 'low'
            findings.append(_f(f'[{tool_name}] URL: {line[:120]}', sev, line, url=line))
        return findings

    # ── Dir discovery — each path = 1 finding ───────────────────────────
    if tool_id in ('gobuster','dirb','dirsearch','feroxbuster'):
        import re as _re
        for line in lines:
            m = _re.search(r'(https?://\S+|/\S+)', line)
            if not m:
                continue
            path = m.group(1)
            sev = ('high' if any(k in path.lower() for k in ['/admin','/config','/.env','/backup','/db','/secret','/login']) else
                   'medium' if any(k in path.lower() for k in ['/upload','/test','/debug','/.git','/user','/panel']) else 'info')
            st = _re.search(r'\b(200|201|301|302|307|401|403|405|500)\b', line)
            code = f' [{st.group(1)}]' if st else ''
            findings.append(_f(f'[{tool_name}] Path: {path[:80]}{code}', sev, line.strip(), url=path))
        return findings

    # ── FFUF / WFuzz ────────────────────────────────────────────────────
    if tool_id in ('ffuf','wfuzz'):
        import re as _re
        for line in lines:
            if _re.search(r'\b(200|201|301|302|307|401|403|405|500)\b', line):
                findings.append(_f(f'[{tool_name}] {line.strip()[:120]}', 'medium', line.strip()))
        return findings

    # ── Paramspider / Arjun ─────────────────────────────────────────────
    if tool_id in ('paramspider','arjun'):
        for line in lines:
            if '?' in line and '=' in line:
                findings.append(_f(f'[{tool_name}] Param URL: {line.strip()[:120]}', 'low', line.strip(), url=line.strip()))
            elif any(k in line.lower() for k in ['parameter','[+]','found']):
                findings.append(_f(f'[{tool_name}] {line.strip()[:120]}', 'low', line.strip()))
        return findings

    # ── Subjack ─────────────────────────────────────────────────────────
    if tool_id == 'subjack':
        for line in lines:
            if any(k in line.lower() for k in ['vulnerable','takeover']):
                findings.append(_f(f'[Subjack] Takeover: {line.strip()[:100]}', 'high', line.strip()))
            elif line.strip():
                findings.append(_f(f'[Subjack] {line.strip()[:100]}', 'info', line.strip()))
        return findings

    # ── SQLMap ──────────────────────────────────────────────────────────
    if tool_id == 'sqlmap':
        for line in lines:
            ll = line.lower()
            if 'is vulnerable' in ll or 'injectable' in ll or '[critical]' in ll:
                findings.append(_f('[SQLMap] SQL Injection confirmed', 'critical', line.strip()))
            elif 'parameter' in ll and 'appears to be' in ll:
                findings.append(_f(f'[SQLMap] Injectable param: {line.strip()[:100]}', 'high', line.strip()))
            elif 'back-end dbms' in ll:
                findings.append(_f(f'[SQLMap] DBMS: {line.strip()[:100]}', 'medium', line.strip()))
        return findings

    # ── Dalfox ──────────────────────────────────────────────────────────
    if tool_id == 'dalfox':
        for line in lines:
            ll = line.lower()
            if any(k in ll for k in ['poc','vuln','xss']):
                findings.append(_f(f'[Dalfox] XSS: {line.strip()[:120]}', 'critical' if 'poc' in ll else 'high', line.strip()))
        return findings

    # ── XSStrike ────────────────────────────────────────────────────────
    if tool_id == 'xsstrike':
        for line in lines:
            if any(k in line.lower() for k in ['vulnerable','xss','payload']):
                findings.append(_f(f'[XSStrike] {line.strip()[:120]}', 'high', line.strip()))
        return findings

    # ── Commix ──────────────────────────────────────────────────────────
    if tool_id == 'commix':
        for line in lines:
            ll = line.lower()
            if any(k in ll for k in ['vulnerable','injection','shell']):
                findings.append(_f(f'[Commix] Cmd injection: {line.strip()[:120]}', 'critical' if 'shell' in ll else 'high', line.strip()))
        return findings

    # ── Tplmap ──────────────────────────────────────────────────────────
    if tool_id == 'tplmap':
        for line in lines:
            if any(k in line.lower() for k in ['vulnerable','code execution','injection']):
                findings.append(_f(f'[Tplmap] SSTI: {line.strip()[:120]}', 'critical', line.strip()))
        return findings

    # ── SSL tools ───────────────────────────────────────────────────────
    if tool_id in ('sslscan','sslyze','testssl'):
        SEV = {'heartbleed':'critical','poodle':'high','beast':'high','crime':'high','null cipher':'critical',
               'expired':'high','self-signed':'high','vulnerable':'high','sslv2':'high','sslv3':'high',
               'rc4':'high','des':'high','weak':'medium','tlsv1.0':'medium','tlsv1.1':'low',
               'deprecated':'medium','insecure':'medium','md5':'medium'}
        for line in lines:
            ll = line.lower()
            sev = next((v for k,v in SEV.items() if k in ll), None)
            if sev:
                findings.append(_f(f'[{tool_name}] {line.strip()[:120]}', sev, line.strip()))
        if not findings:
            findings.append(_f(f'[{tool_name}] SSL/TLS scan — no critical issues', 'info', f'{len(lines)} lines analyzed'))
        return findings

    # ── WPScan ──────────────────────────────────────────────────────────
    if tool_id == 'wpscan':
        for line in lines:
            ll = line.lower()
            if 'vulnerability' in ll or '[!]' in line:
                findings.append(_f(f'[WPScan] {line.strip()[:120]}', 'high', line.strip()))
            elif ('version' in ll and ('detected' in ll or 'found' in ll)) or ('user' in ll and 'found' in ll):
                findings.append(_f(f'[WPScan] {line.strip()[:120]}', 'medium', line.strip()))
        return findings

    # ── Droopescan / Joomscan ───────────────────────────────────────────
    if tool_id in ('droopescan','joomscan'):
        for line in lines:
            ll = line.lower()
            if any(k in ll for k in ['vulnerability','version','found','detected','exposed']):
                sev = 'high' if 'vuln' in ll else 'medium' if 'version' in ll else 'info'
                findings.append(_f(f'[{tool_name}] {line.strip()[:120]}', sev, line.strip()))
        return findings

    # ── Hydra / Medusa ──────────────────────────────────────────────────
    if tool_id in ('hydra','medusa'):
        for line in lines:
            if any(k in line.lower() for k in ['login:','password:','success']):
                findings.append(_f(f'[{tool_name}] Credential found: {line.strip()[:150]}', 'critical', line.strip()))
        return findings

    # ── Bandit ──────────────────────────────────────────────────────────
    if tool_id == 'bandit':
        import re as _re
        cur = {}
        for line in lines:
            if 'Severity:' in line:
                m = _re.search(r'Severity:\s*(\w+)', line)
                if m: cur['sev'] = m.group(1).lower()
            if 'Issue:' in line:
                cur['issue'] = line.split('Issue:',1)[-1].strip()
            if 'Location:' in line and cur.get('issue'):
                loc = line.split('Location:',1)[-1].strip()
                findings.append(_f(f'[Bandit] {cur["issue"][:80]}', cur.get("sev","medium"),
                                   f'{cur["issue"]} at {loc}', file_path=loc))
                cur = {}
        return findings

    # ── Semgrep ─────────────────────────────────────────────────────────
    if tool_id == 'semgrep':
        import re as _re
        for line in lines:
            m = _re.match(r'(.+?):(\d+):\s*(\S+):\s*(.+)', line)
            if m:
                fpath, lineno, rule, msg = m.groups()
                sev = 'high' if any(k in rule for k in ['injection','exec','shell','xss','sqli']) else 'medium'
                findings.append(_f(f'[Semgrep] {rule}: {msg[:80]}', sev,
                                   f'{fpath}:{lineno} — {msg}', file_path=fpath))
        return findings

    # ── Gitleaks ────────────────────────────────────────────────────────
    if tool_id == 'gitleaks':
        for line in lines:
            ll = line.lower()
            if any(k in ll for k in ['secret','token','key','password','credential','leak','finding']):
                sev = 'critical' if any(k in ll for k in ['secret','token','credential']) else 'high'
                findings.append(_f(f'[Gitleaks] {line.strip()[:120]}', sev, line.strip()))
        return findings

    # ── TruffleHog ──────────────────────────────────────────────────────
    if tool_id == 'trufflehog':
        for line in lines:
            ll = line.lower()
            if any(k in ll for k in ['found','secret','detector','verified','raw']):
                findings.append(_f(f'[TruffleHog] {line.strip()[:120]}',
                                   'critical' if 'verified' in ll else 'high', line.strip()))
        return findings

    # ── detect-secrets ──────────────────────────────────────────────────
    if tool_id == 'detect_secrets':
        import json as _json
        try:
            data = _json.loads(output_text)
            for fname, secrets in data.get('results', {}).items():
                for s in secrets:
                    findings.append(_f(f'[detect-secrets] {s.get("type","Secret")} in {fname}', 'high',
                                       f'Line {s.get("line_number","?")} in {fname}', file_path=fname))
        except Exception:
            for line in lines:
                if line.strip():
                    findings.append(_f(f'[detect-secrets] {line.strip()[:120]}', 'high', line.strip()))
        return findings

    # ── dnsx ────────────────────────────────────────────────────────────
    if tool_id == 'dnsx':
        for line in lines:
            if line.strip():
                findings.append(_f(f'[dnsx] {line.strip()[:100]}', 'info', line.strip()))
        return findings

    # ── Interactsh ──────────────────────────────────────────────────────
    if tool_id == 'interactsh_client':
        for line in lines:
            if any(k in line.lower() for k in ['interaction','received','oob']):
                findings.append(_f(f'[Interactsh] OOB: {line.strip()[:120]}', 'high', line.strip()))
        return findings

    # ── Generic fallback — severity-classified per line ─────────────────
    SEV_KWS = {
        'critical': ['critical','rce','remote code','shell','exploit','backdoor'],
        'high':     ['vuln','vulnerable','xss','sqli','injection','leak','exposed','takeover','heap'],
        'medium':   ['warning','found','detected','weak','misconfigured','missing header','open redirect'],
        'low':      ['info','version','cookie','redirect','deprecated','allowed'],
    }
    for line in lines[:300]:
        line = line.strip()
        if not line or len(line) < 6:
            continue
        ll = line.lower()
        sev = 'info'
        for s, kws in SEV_KWS.items():
            if any(k in ll for k in kws):
                sev = s
                break
        findings.append(_f(f'[{tool_name}] {line[:120]}', sev, line))
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

    def _build_expanded_targets(self):
        """
        After Phase 1 recon, extract from findings + raw tool output:
          - subdomains   → test with web vuln tools
          - param_urls   → test with SQLi/XSS/injection tools
          - endpoints    → test with dir scanners / vuln tools
          - open_ports   → context info
        Returns dict with sets of strings.
        """
        from urllib.parse import urlparse, urljoin
        expanded = {
            'subdomains': set(),    # 'sub.example.com'
            'param_urls': set(),    # 'http://x.com/p?id=1'
            'endpoints': set(),     # 'http://x.com/admin'
            'open_ports': [],       # (port_str, service)
        }
        import re as _re

        base_domain = _extract_domain(self.target)
        base_url = self.target if _is_url(self.target) else f'http://{self.target}'

        def _looks_like_subdomain(s):
            return bool(s and '.' in s and not s.startswith('http')
                        and base_domain in s and len(s) < 200)

        # ── 1. Mine raw tool stdout outputs ─────────────────────────────
        subdomain_tools = ('subfinder','amass','findomain','assetfinder','chaos','github_subdomains')
        for tid in subdomain_tools:
            for line in self._tool_outputs.get(tid, '').split('\n'):
                s = line.strip().lower()
                if _looks_like_subdomain(s):
                    expanded['subdomains'].add(s)

        param_url_tools = ('waybackurls','gau','katana','hakrawler','paramspider','arjun')
        for tid in param_url_tools:
            for line in self._tool_outputs.get(tid, '').split('\n'):
                line = line.strip()
                if line.startswith('http') and '?' in line and '=' in line:
                    expanded['param_urls'].add(line)
                elif '?' in line and '=' in line and not line.startswith('http'):
                    full = base_url.rstrip('/') + '/' + line.lstrip('/')
                    expanded['param_urls'].add(full)

        dir_tools = ('gobuster','dirb','dirsearch','feroxbuster','ffuf','wfuzz')
        for tid in dir_tools:
            for line in self._tool_outputs.get(tid, '').split('\n'):
                m = _re.search(r'(https?://\S+|/\S+)', line)
                if m:
                    path = m.group(1)
                    if path.startswith('http') and base_domain in path:
                        expanded['endpoints'].add(path.split('#')[0])
                    elif path.startswith('/'):
                        expanded['endpoints'].add(base_url.rstrip('/') + path.split('?')[0])

        # ── 2. Mine structured findings ─────────────────────────────────
        for f in self.all_findings:
            desc = f.get('description', '')

            # subdomains embedded in description
            for line in desc.split('\n'):
                s = line.strip().lower()
                if _looks_like_subdomain(s):
                    expanded['subdomains'].add(s)

            # URLs with params
            if f.get('url'):
                url = f['url']
                if '?' in url and '=' in url:
                    expanded['param_urls'].add(url)
                elif url.startswith('http') and base_domain in url:
                    expanded['endpoints'].add(url)

            # Open ports from Nmap findings
            if f.get('port') and f.get('service'):
                expanded['open_ports'].append((f['port'], f.get('service','')))

        # ── 3. Build subdomain URLs ──────────────────────────────────────
        # Convert subdomains to full URLs for web tools
        subdomain_urls = set()
        for sub in expanded['subdomains']:
            if not sub.startswith('http'):
                subdomain_urls.add(f'https://{sub}')
                subdomain_urls.add(f'http://{sub}')
        expanded['subdomain_urls'] = subdomain_urls

        # ── 4. Deduplicate & cap (avoid infinite scan) ───────────────────
        MAX_SUBDOMAINS = 15
        MAX_PARAM_URLS = 30
        MAX_ENDPOINTS  = 20

        expanded['subdomains']    = set(list(expanded['subdomains'])[:MAX_SUBDOMAINS])
        expanded['subdomain_urls']= set(list(expanded['subdomain_urls'])[:MAX_SUBDOMAINS*2])
        expanded['param_urls']    = set(list(expanded['param_urls'])[:MAX_PARAM_URLS])
        expanded['endpoints']     = set(list(expanded['endpoints'])[:MAX_ENDPOINTS])

        # Write subdomains to temp file for subjack pipeline
        if expanded['subdomains']:
            subs_file = os.path.join(
                self._context.get('temp_dir', tempfile.gettempdir()),
                'emyuel_subdomains.txt'
            )
            try:
                with open(subs_file, 'w') as fp:
                    fp.write('\n'.join(expanded['subdomains']))
                self._context['subdomains_file'] = subs_file
            except Exception:
                pass

        return expanded

    def _run_vuln_on_expanded(self, vuln_tools_runnable, expanded):
        """
        For each vuln tool, run it against appropriate expanded targets
        discovered during recon (subdomains, param URLs, endpoints).
        Returns additional findings list.
        """
        extra_findings = []
        if not vuln_tools_runnable:
            return extra_findings

        PARAM_URL_TOOLS = {'sqlmap', 'dalfox', 'xsstrike', 'commix', 'tplmap', 'ssrfmap', 'arjun'}
        SUBDOMAIN_TOOLS = {'nuclei', 'nikto', 'wapiti', 'whatweb', 'wpscan', 'droopescan',
                           'joomscan', 'sslscan', 'sslyze', 'testssl', 'gobuster', 'dirsearch',
                           'feroxbuster', 'ffuf', 'dirb', 'httpx_tool'}
        ENDPOINT_TOOLS  = {'dalfox', 'xsstrike', 'sqlmap', 'commix', 'nikto', 'nuclei'}

        ts = datetime.now().strftime('%H:%M:%S')
        self.log(f'\n[{ts}] 🎯 Phase 2b — Vuln testing expanded targets...')

        tasks = []
        orig_norm = self.target.rstrip('/')

        for tool_id, info, _orig_cmd, timeout, _orig_stdin in vuln_tools_runnable:
            targets_for_tool = set()
            if tool_id in PARAM_URL_TOOLS:
                targets_for_tool.update(expanded['param_urls'])
            if tool_id in SUBDOMAIN_TOOLS:
                targets_for_tool.update(expanded['subdomain_urls'])
            if tool_id in ENDPOINT_TOOLS:
                targets_for_tool.update(expanded['endpoints'])

            # Exclude original target (already scanned in Phase 2a)
            targets_for_tool.discard(orig_norm)
            targets_for_tool.discard(orig_norm + '/')

            for exp_target in targets_for_tool:
                built = _build_cmd(tool_id, exp_target, self._context)
                if built is None:
                    continue
                cmd_list, to, stdin = built
                resolved = _resolve_cmd(cmd_list[0])
                if not resolved:
                    continue
                cmd_list[0] = resolved
                tasks.append((tool_id, info, cmd_list, to, stdin, exp_target))

        if not tasks:
            self.log('  ℹ️  No expanded targets applicable for selected vuln tools')
            return extra_findings

        self.log(f'  🔬 Running {len(tasks)} additional targeted scans on expanded attack surface...')

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(self._run_single, tool_id, info, cmd, to, stdin): (tool_id, exp_target)
                for tool_id, info, cmd, to, stdin, exp_target in tasks
            }
            for future in as_completed(futures):
                tool_id, exp_target = futures[future]
                try:
                    results = future.result(timeout=660)
                    extra_findings.extend(results)
                except Exception as e:
                    self.log(f'  ⚠️  {tool_id} on {exp_target[:60]}: {e}')

        ts = datetime.now().strftime('%H:%M:%S')
        self.log(f'[{ts}] ✅ Phase 2b complete: +{len(extra_findings)} findings from expanded targets')
        return extra_findings

    def run_all(self):
        """Run tools in two phases: Recon first, then Vuln Testing."""
        # ── Categories that make up Phase 1 (Recon / Discovery) ───
        RECON_CATEGORIES = {
            'Network Scanner', 'Port Scanner', 'Subdomain',
            'Subdomain Takeover', 'OSINT/Recon', 'HTTP Probe',
            'DNS Recon', 'Web Recon', 'Web Crawler',
            'Visual Recon', 'Fingerprinting', 'URL Manipulation',
            'Pattern Grep', 'Param Discovery', 'Dir Discovery',
            'Dir Scanner', 'API Testing', 'SSL/TLS', 'Wordlists',
        }

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

        # ── Split into phases ────────────────────────────────────
        recon_tools = [
            t for t in runnable
            if t[1].get('category', '') in RECON_CATEGORIES
        ]
        vuln_tools = [
            t for t in runnable
            if t[1].get('category', '') not in RECON_CATEGORIES
        ]

        # ── Phase 1: Recon ───────────────────────────────────────
        if recon_tools:
            recon_names = ', '.join(info['name'] for _, info, _, _, _ in recon_tools)
            self.log(f"\n[{ts}] 🔍 Phase 1 — Recon ({len(recon_tools)} tools)")
            self.log(f"  Running: {recon_names}")

            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                futures = {
                    executor.submit(self._run_single, tool_id, info, cmd_list, timeout, stdin_data): tool_id
                    for tool_id, info, cmd_list, timeout, stdin_data in recon_tools
                }
                for future in as_completed(futures):
                    tool_id = futures[future]
                    try:
                        findings = future.result(timeout=600)
                        self.all_findings.extend(findings)
                    except Exception as e:
                        self.log(f"  ❌ {tool_id}: unhandled error: {e}")

            ts = datetime.now().strftime('%H:%M:%S')
            self.log(f"[{ts}] ✅ Phase 1 complete: {len(self.all_findings)} recon findings")

        # ── After Phase 1: analyze recon output, expand target surface ──
        expanded = self._build_expanded_targets()
        sub_count   = len(expanded['subdomains'])
        param_count = len(expanded['param_urls'])
        ep_count    = len(expanded['endpoints'])
        port_count  = len(expanded['open_ports'])

        ts = datetime.now().strftime('%H:%M:%S')
        self.log(f'\n[{ts}] 🗺️  Recon Analysis — Expanded Attack Surface:')
        self.log(f'  📡 {sub_count} subdomains  |  🔗 {param_count} param URLs  |  📂 {ep_count} endpoints  |  🔌 {port_count} open ports')

        # ── Phase 2a: Vuln Testing on original target ─────────────────

        # ── Phase 2: Vuln Testing ────────────────────────────────
        if vuln_tools:
            ts = datetime.now().strftime('%H:%M:%S')
            vuln_names = ', '.join(info['name'] for _, info, _, _, _ in vuln_tools)
            self.log(f"\n[{ts}] ⚔️ Phase 2a — Vuln Testing original target ({len(vuln_tools)} tools)")
            self.log(f"  Running: {vuln_names}")

            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                futures = {
                    executor.submit(self._run_single, tool_id, info, cmd_list, timeout, stdin_data): tool_id
                    for tool_id, info, cmd_list, timeout, stdin_data in vuln_tools
                }
                for future in as_completed(futures):
                    tool_id = futures[future]
                    try:
                        findings = future.result(timeout=600)
                        self.all_findings.extend(findings)
                    except Exception as e:
                        self.log(f"  ❌ {tool_id}: unhandled error: {e}")

            ts = datetime.now().strftime('%H:%M:%S')
            self.log(f"[{ts}] ✅ Phase 2a complete")

            # ── Phase 2b: expanded vuln testing on recon-discovered targets
            expanded_findings = self._run_vuln_on_expanded(vuln_tools, expanded)
            self.all_findings.extend(expanded_findings)

        # ── Pipeline Chains (post-scan) ──────────────────────────
        self._run_pipelines()

        ts = datetime.now().strftime('%H:%M:%S')
        self.log(f"[{ts}] ✅ All phases complete: {len(self.all_findings)} findings total")
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

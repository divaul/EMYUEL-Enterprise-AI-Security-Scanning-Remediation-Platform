"""
tool_executor.py — External security tool execution engine for EMYUEL

Runs selected CLI security tools against scan targets via subprocess,
parses output into unified findings, and reports progress in real-time.
"""

import subprocess
import shutil
import os
import re
import pathlib
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse


# ─── Command Builders ─────────────────────────────────────────────
# Each function returns (cmd_list, timeout_seconds) or None if tool not applicable.

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


# Map of tool_id → function(target) → (cmd_list, timeout)
TOOL_COMMANDS = {
    # ─── Network Scanners
    'nmap': lambda t: (['nmap', '-sV', '-sC', '--top-ports', '100', '-T4', _extract_domain(t)], 120),
    'masscan': lambda t: (['masscan', _extract_domain(t), '-p1-1000', '--rate=1000'], 120),
    'rustscan': lambda t: (['rustscan', '-a', _extract_domain(t), '--', '-sV'], 120),
    'naabu': lambda t: (['naabu', '-host', _extract_domain(t), '-top-ports', '100'], 90),

    # ─── Web Scanners
    'nikto': lambda t: (['nikto', '-h', t, '-maxtime', '120'], 150) if _is_url(t) else None,
    'wapiti': lambda t: (['wapiti', '-u', t, '--flush-session', '-m', 'common', '--max-scan-time', '120'], 150) if _is_url(t) else None,
    'skipfish': lambda t: None,  # Requires output dir, skip for auto
    'whatweb': lambda t: (['whatweb', '-v', t], 60) if _is_url(t) else None,

    # ─── SQL Injection
    'sqlmap': lambda t: (['sqlmap', '-u', t, '--batch', '--level=1', '--risk=1', '--timeout=30'], 180) if _is_url(t) else None,

    # ─── XSS
    'dalfox': lambda t: (['dalfox', 'url', t, '--silence'], 120) if _is_url(t) else None,
    'xsstrike': lambda t: (['xsstrike', '-u', t, '--skip'], 120) if _is_url(t) else None,

    # ─── SSTI / SSRF
    'tplmap': lambda t: (['tplmap', '-u', t], 120) if _is_url(t) else None,
    'ssrfmap': lambda t: None,  # Requires specific params, skip for auto

    # ─── Dir Discovery
    'gobuster': lambda t: (['gobuster', 'dir', '-u', t, '-w', '/usr/share/wordlists/dirb/common.txt', '-q', '-t', '20'], 120) if _is_url(t) else None,
    'dirb': lambda t: (['dirb', t, '-S', '-r'], 120) if _is_url(t) else None,
    'dirsearch': lambda t: (['dirsearch', '-u', t, '--quiet', '-t', '20'], 120) if _is_url(t) else None,
    'feroxbuster': lambda t: (['feroxbuster', '-u', t, '-q', '--time-limit', '120s'], 150) if _is_url(t) else None,

    # ─── Fuzzing
    'ffuf': lambda t: (['ffuf', '-u', t + '/FUZZ', '-w', '/usr/share/wordlists/dirb/common.txt', '-mc', '200,301,302,403', '-t', '20'], 120) if _is_url(t) else None,
    'wfuzz': lambda t: (['wfuzz', '-c', '--hc', '404', '-w', '/usr/share/wordlists/dirb/common.txt', t + '/FUZZ'], 120) if _is_url(t) else None,

    # ─── Brute Force
    'hydra': lambda t: None,  # Requires creds/protocol, skip
    'medusa': lambda t: None,  # Requires creds/protocol, skip
    'john': lambda t: None,    # Requires hash file
    'hashcat': lambda t: None, # Requires hash file

    # ─── CMS
    'wpscan': lambda t: (['wpscan', '--url', t, '--enumerate', 'vp,vt,u', '--no-banner'], 180) if _is_url(t) else None,
    'droopescan': lambda t: (['droopescan', 'scan', '-u', t], 120) if _is_url(t) else None,
    'joomscan': lambda t: (['joomscan', '-u', t], 120) if _is_url(t) else None,

    # ─── Subdomain & Recon
    'subfinder': lambda t: (['subfinder', '-d', _extract_domain(t), '-silent'], 90),
    'amass': lambda t: (['amass', 'enum', '-d', _extract_domain(t), '-passive', '-timeout', '2'], 180),
    'findomain': lambda t: (['findomain', '-t', _extract_domain(t), '-q'], 90),
    'chaos': lambda t: (['chaos', '-d', _extract_domain(t), '-silent'], 60),
    'github_subdomains': lambda t: (['github-subdomains', '-d', _extract_domain(t)], 90),
    'subjack': lambda t: None,  # Requires subdomain list file
    'assetfinder': lambda t: (['assetfinder', '--subs-only', _extract_domain(t)], 60),

    # ─── HTTP Probing
    'httpx_tool': lambda t: (['httpx', '-u', t, '-silent', '-status-code', '-title', '-tech-detect'], 60),
    'httprobe': lambda t: None,  # Requires stdin list

    # ─── Vulnerability Scanning
    'nuclei': lambda t: (['nuclei', '-u', t, '-severity', 'low,medium,high,critical', '-silent', '-nc'], 300) if _is_url(t) else None,
    'openvas': lambda t: None,  # Requires full setup
    'interactsh_client': lambda t: None,  # OOB server, not direct scan

    # ─── SSL/TLS
    'sslscan': lambda t: (['sslscan', '--no-colour', _extract_domain(t)], 60),
    'sslyze': lambda t: (['sslyze', _extract_domain(t)], 90),
    'testssl': lambda t: (['testssl', '--quiet', '--color', '0', _extract_domain(t)], 120),

    # ─── Command Injection
    'commix': lambda t: (['commix', '-u', t, '--batch', '--level=1'], 120) if _is_url(t) else None,

    # ─── Param Discovery / URL Manipulation
    'paramspider': lambda t: (['paramspider', '-d', _extract_domain(t)], 90),
    'arjun': lambda t: (['arjun', '-u', t, '-q'], 120) if _is_url(t) else None,
    'qsreplace': lambda t: None,  # Requires stdin
    'unfurl': lambda t: None,     # Requires stdin
    'gf': lambda t: None,         # Requires stdin

    # ─── Web Recon / URL Collection
    'waybackurls': lambda t: (['waybackurls', _extract_domain(t)], 60),
    'gau': lambda t: (['gau', _extract_domain(t)], 60),
    'hakrawler': lambda t: None,  # Requires stdin
    'katana': lambda t: (['katana', '-u', t, '-silent', '-d', '2'], 120) if _is_url(t) else None,

    # ─── Visual Recon
    'aquatone': lambda t: None,   # Requires stdin pipe
    'gowitness': lambda t: (['gowitness', 'single', t], 60) if _is_url(t) else None,

    # ─── DNS Recon
    'dnsx': lambda t: (['dnsx', '-d', _extract_domain(t), '-silent'], 60),
    'shuffledns': lambda t: None, # Requires wordlist + resolver

    # ─── SAST (for local paths)
    'semgrep': lambda t: (['semgrep', 'scan', '--config=auto', '--quiet', t], 180) if _is_path(t) else None,
    'bandit': lambda t: (['bandit', '-r', t, '-q', '-f', 'screen'], 120) if _is_path(t) else None,
    'brakeman': lambda t: (['brakeman', '-q', '-p', t], 120) if _is_path(t) else None,

    # ─── Secret Scanning (for local paths)
    'gitleaks': lambda t: (['gitleaks', 'detect', '--source', t, '--no-banner'], 120) if _is_path(t) else None,
    'trufflehog': lambda t: (['trufflehog', 'filesystem', t, '--no-update'], 120) if _is_path(t) else None,
    'detect_secrets': lambda t: (['detect-secrets', 'scan', t], 90) if _is_path(t) else None,

    # ─── Wordlists (not executable)
    'seclists': lambda t: None,

    # ─── Exploitation
    'searchsploit': lambda t: (['searchsploit', _extract_domain(t)], 30),

    # ─── Web Proxy (interactive, not auto-runnable)
    'burpsuite': lambda t: None,
    'owasp_zap': lambda t: None,  # Could use zap-cli but needs daemon running
    'mitmproxy': lambda t: None,

    # ─── API Testing
    'newman': lambda t: None,     # Requires Postman collection
    'kiterunner': lambda t: (['kr', 'brute', t, '-w', '/usr/share/wordlists/dirb/common.txt'], 120) if _is_url(t) else None,

    # ─── Python libraries / AI SDKs (not CLI tools)
    'aiohttp': lambda t: None,
    'httpx_pkg': lambda t: None,
    'requests': lambda t: None,
    'beautifulsoup': lambda t: None,
    'scrapy': lambda t: None,
    'google_genai': lambda t: None,
    'openai_sdk': lambda t: None,
    'anthropic_sdk': lambda t: None,

    # ─── Reporting (not scan tools)
    'dradis': lambda t: None,
    'faraday': lambda t: None,
    'defectdojo': lambda t: None,
}


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


def _parse_output_to_findings(tool_id, tool_name, output_text, target):
    """Convert raw tool output into structured findings list."""
    findings = []

    if not output_text or not output_text.strip():
        return findings

    lines = output_text.strip().split('\n')

    # Nuclei has structured output: [severity] [template-id] [protocol] target
    if tool_id == 'nuclei':
        for line in lines:
            line = line.strip()
            if not line:
                continue
            # Nuclei silent output: [template-id] [protocol] [severity] url
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

    # Nmap — look for open ports
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

    # Subfinder/Amass/Assetfinder — each line is a subdomain
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

    # Waybackurls/gau/katana — each line is a URL
    if tool_id in ('waybackurls', 'gau', 'katana'):
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

    # SQLMap — look for injection confirmations
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

    # Dalfox — XSS findings
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

    # Bandit — Python security issues
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

    # Gitleaks — secret detection
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

    # Generic — report full output as a single finding
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


class ToolExecutor:
    """
    Executes external security tools against a target.

    Usage:
        executor = ToolExecutor(target, selected_tools, tool_registry, log_fn)
        findings = executor.run_all()  # Blocking, runs tools concurrently
    """

    def __init__(self, target, selected_tool_ids, tool_registry, log_fn=None, max_workers=5):
        self.target = target
        self.selected_tool_ids = selected_tool_ids
        self.tool_registry = tool_registry
        self.log = log_fn or (lambda msg: None)
        self.max_workers = max_workers
        self.all_findings = []

    def run_all(self):
        """Run all selected tools concurrently. Returns list of findings."""
        runnable = []
        skipped_not_installed = []
        skipped_no_cmd = []

        for tool_id in self.selected_tool_ids:
            info = self.tool_registry.get(tool_id)
            if not info:
                continue

            # Check if this tool has a command builder
            builder = TOOL_COMMANDS.get(tool_id)
            if not builder:
                skipped_no_cmd.append(info['name'])
                continue

            # Build command
            try:
                result = builder(self.target)
            except Exception:
                result = None

            if result is None:
                skipped_no_cmd.append(info['name'])
                continue

            cmd_list, timeout = result

            # Check if tool is installed
            cmd_exe = cmd_list[0]
            resolved = _resolve_cmd(cmd_exe)
            if not resolved:
                skipped_not_installed.append(info['name'])
                continue

            # Replace command name with full path
            cmd_list[0] = resolved
            runnable.append((tool_id, info, cmd_list, timeout))

        # Log summary
        ts = datetime.now().strftime('%H:%M:%S')
        self.log(f"\n[{ts}] 🔧 External Tools: {len(runnable)} runnable, "
                 f"{len(skipped_not_installed)} not installed, "
                 f"{len(skipped_no_cmd)} not applicable")

        if skipped_not_installed:
            self.log(f"  ⚠️ Not installed: {', '.join(skipped_not_installed[:10])}"
                     + (f' +{len(skipped_not_installed)-10} more' if len(skipped_not_installed) > 10 else ''))

        if not runnable:
            self.log(f"[{ts}] ℹ️ No external tools to run.")
            return []

        # Run concurrently
        self.log(f"[{ts}] 🚀 Running: {', '.join(info['name'] for _, info, _, _ in runnable)}")

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(self._run_single, tool_id, info, cmd_list, timeout): tool_id
                for tool_id, info, cmd_list, timeout in runnable
            }
            for future in as_completed(futures):
                tool_id = futures[future]
                try:
                    findings = future.result(timeout=600)
                    self.all_findings.extend(findings)
                except Exception as e:
                    self.log(f"  ❌ {tool_id}: unhandled error: {e}")

        ts = datetime.now().strftime('%H:%M:%S')
        self.log(f"[{ts}] ✅ External tools complete: {len(self.all_findings)} findings")
        return self.all_findings

    def _run_single(self, tool_id, info, cmd_list, timeout):
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
                env={**os.environ, 'TERM': 'dumb', 'NO_COLOR': '1'},
            )
            output = (result.stdout or '') + (result.stderr or '')
            exit_code = result.returncode

            ts2 = datetime.now().strftime('%H:%M:%S')

            if exit_code == 0 or output.strip():
                lines = len(output.strip().split('\n')) if output.strip() else 0
                self.log(f"  [{ts2}] ✅ {tool_name} — {lines} lines output")
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

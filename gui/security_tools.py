"""
security_tools.py — Shared cybersecurity tools registry for EMYUEL

Central registry of all supported security tools with install/detect metadata.
Used by AI Analysis, Quick Scan, and Advanced Scan tabs.
Focused on web application security testing — no wireless, forensics, RE, or infra tools.
"""

SECURITY_TOOLS = {
    # ─── Network Scanners ──────────────────────────
    'nmap': {
        'name': 'Nmap', 'icon': '🌐', 'category': 'Network Scanner',
        'desc': 'Network exploration and security auditing',
        'check_cmd': 'nmap', 'install_apt': 'nmap', 'install_pip': None,
        'usable_in': ['quick', 'advanced', 'ai'],
    },
    'masscan': {
        'name': 'Masscan', 'icon': '🚀', 'category': 'Port Scanner',
        'desc': 'High-speed TCP port scanner (10M packets/sec)',
        'check_cmd': 'masscan', 'install_apt': 'masscan', 'install_pip': None,
        'usable_in': ['advanced', 'ai'],
    },
    'rustscan': {
        'name': 'RustScan', 'icon': '⚡', 'category': 'Port Scanner',
        'desc': 'Ultra-fast port scanner (Rust) with Nmap integration',
        'check_cmd': 'rustscan', 'install_apt': None, 'install_pip': None,
        'install_custom': 'cargo install rustscan',
        'usable_in': ['advanced', 'ai'],
    },
    'naabu': {
        'name': 'Naabu', 'icon': '🎯', 'category': 'Port Scanner',
        'desc': 'Fast port scanning tool (ProjectDiscovery)',
        'check_cmd': 'naabu', 'install_apt': None, 'install_pip': None,
        'install_custom': 'go install -v github.com/projectdiscovery/naabu/v2/cmd/naabu@latest',
        'usable_in': ['quick', 'advanced', 'ai'],
    },

    # ─── Web Scanners ──────────────────────────────
    'nikto': {
        'name': 'Nikto', 'icon': '🔍', 'category': 'Web Scanner',
        'desc': 'Web server scanner for dangerous files/CGIs',
        'check_cmd': 'nikto', 'install_apt': 'nikto', 'install_pip': None,
        'usable_in': ['quick', 'advanced', 'ai'],
    },
    'wapiti': {
        'name': 'Wapiti', 'icon': '🕷️', 'category': 'Web Scanner',
        'desc': 'Black-box web application vulnerability scanner',
        'check_cmd': 'wapiti', 'install_apt': None, 'install_pip': 'wapiti3',
        'usable_in': ['quick', 'advanced', 'ai'],
    },
    'skipfish': {
        'name': 'Skipfish', 'icon': '🐟', 'category': 'Web Scanner',
        'desc': 'Active web application security reconnaissance by Google',
        'check_cmd': 'skipfish', 'install_apt': 'skipfish', 'install_pip': None,
        'usable_in': ['advanced', 'ai'],
    },
    'whatweb': {
        'name': 'WhatWeb', 'icon': '🔎', 'category': 'Fingerprinting',
        'desc': 'Web technology identification and fingerprinting',
        'check_cmd': 'whatweb', 'install_apt': 'whatweb', 'install_pip': None,
        'usable_in': ['quick', 'advanced', 'ai'],
    },

    # ─── SQL Injection ─────────────────────────────
    'sqlmap': {
        'name': 'SQLMap', 'icon': '🗄️', 'category': 'SQL Injection',
        'desc': 'Automatic SQL injection and database takeover',
        'check_cmd': 'sqlmap', 'install_apt': 'sqlmap', 'install_pip': 'sqlmap',
        'usable_in': ['quick', 'advanced', 'ai'],
    },

    # ─── XSS Testing ──────────────────────────────
    'dalfox': {
        'name': 'Dalfox', 'icon': '🦊', 'category': 'XSS Scanner',
        'desc': 'Parameter analysis and XSS scanning tool (Go)',
        'check_cmd': 'dalfox', 'install_apt': None, 'install_pip': None,
        'install_custom': 'go install github.com/hahwul/dalfox/v2@latest',
        'usable_in': ['quick', 'advanced', 'ai'],
    },
    'xsstrike': {
        'name': 'XSStrike', 'icon': '💥', 'category': 'XSS Scanner',
        'desc': 'Advanced XSS detection suite with fuzzing engine',
        'check_cmd': 'xsstrike', 'install_apt': None, 'install_pip': 'xsstrike',
        'usable_in': ['quick', 'advanced', 'ai'],
    },

    # ─── SSRF / SSTI / Template Injection ──────────
    'tplmap': {
        'name': 'Tplmap', 'icon': '🗺️', 'category': 'SSTI Scanner',
        'desc': 'Server-Side Template Injection detection and exploitation',
        'check_cmd': 'tplmap', 'install_apt': None, 'install_pip': None,
        'install_custom': 'pip install tplmap',
        'usable_in': ['advanced', 'ai'],
    },
    'ssrfmap': {
        'name': 'SSRFmap', 'icon': '🔄', 'category': 'SSRF Scanner',
        'desc': 'Automatic SSRF fuzzer and exploitation tool',
        'check_cmd': 'ssrfmap', 'install_apt': None, 'install_pip': None,
        'install_custom': 'pip install ssrfmap',
        'usable_in': ['advanced', 'ai'],
    },

    # ─── Directory & Content Discovery ─────────────
    'gobuster': {
        'name': 'GoBuster', 'icon': '📁', 'category': 'Dir Discovery',
        'desc': 'URI/DNS/VHost brute-forcing tool (Go)',
        'check_cmd': 'gobuster', 'install_apt': 'gobuster', 'install_pip': None,
        'usable_in': ['quick', 'advanced', 'ai'],
    },
    'dirb': {
        'name': 'DIRB', 'icon': '📂', 'category': 'Dir Scanner',
        'desc': 'Web content scanner (dictionary based attack)',
        'check_cmd': 'dirb', 'install_apt': 'dirb', 'install_pip': None,
        'usable_in': ['advanced', 'ai'],
    },
    'dirsearch': {
        'name': 'Dirsearch', 'icon': '🔦', 'category': 'Dir Discovery',
        'desc': 'Advanced web path brute-forcer',
        'check_cmd': 'dirsearch', 'install_apt': None, 'install_pip': 'dirsearch',
        'usable_in': ['quick', 'advanced', 'ai'],
    },
    'feroxbuster': {
        'name': 'Feroxbuster', 'icon': '🦀', 'category': 'Dir Discovery',
        'desc': 'Fast, recursive content discovery tool (Rust)',
        'check_cmd': 'feroxbuster', 'install_apt': None, 'install_pip': None,
        'install_custom': 'cargo install feroxbuster',
        'usable_in': ['advanced', 'ai'],
    },

    # ─── Fuzzing ───────────────────────────────────
    'ffuf': {
        'name': 'FFUF', 'icon': '⚡', 'category': 'Fuzzer',
        'desc': 'Fast web fuzzer written in Go',
        'check_cmd': 'ffuf', 'install_apt': 'ffuf', 'install_pip': None,
        'usable_in': ['advanced', 'ai'],
    },
    'wfuzz': {
        'name': 'Wfuzz', 'icon': '🎯', 'category': 'Web Fuzzer',
        'desc': 'Web application payload fuzzing',
        'check_cmd': 'wfuzz', 'install_apt': None, 'install_pip': 'wfuzz',
        'usable_in': ['advanced', 'ai'],
    },

    # ─── Brute Force / Auth ────────────────────────
    'hydra': {
        'name': 'Hydra', 'icon': '🔐', 'category': 'Brute Force',
        'desc': 'Fast network logon cracker for various protocols',
        'check_cmd': 'hydra', 'install_apt': 'hydra', 'install_pip': None,
        'usable_in': ['advanced', 'ai'],
    },
    'medusa': {
        'name': 'Medusa', 'icon': '🐍', 'category': 'Brute Force',
        'desc': 'Speedy, parallel, modular brute-force login tool',
        'check_cmd': 'medusa', 'install_apt': 'medusa', 'install_pip': None,
        'usable_in': ['advanced', 'ai'],
    },
    'john': {
        'name': 'John the Ripper', 'icon': '🔨', 'category': 'Password Crack',
        'desc': 'Offline password hash cracker',
        'check_cmd': 'john', 'install_apt': 'john', 'install_pip': None,
        'usable_in': ['advanced'],
    },
    'hashcat': {
        'name': 'Hashcat', 'icon': '🏷️', 'category': 'Password Crack',
        'desc': 'GPU-accelerated password recovery (hash cracking)',
        'check_cmd': 'hashcat', 'install_apt': 'hashcat', 'install_pip': None,
        'usable_in': ['advanced'],
    },

    # ─── CMS Specific ─────────────────────────────
    'wpscan': {
        'name': 'WPScan', 'icon': '📝', 'category': 'WordPress',
        'desc': 'WordPress security scanner with vuln DB',
        'check_cmd': 'wpscan', 'install_apt': None, 'install_pip': None,
        'install_custom': 'gem install wpscan',
        'usable_in': ['quick', 'advanced', 'ai'],
    },
    'droopescan': {
        'name': 'Droopescan', 'icon': '💧', 'category': 'CMS Scanner',
        'desc': 'Scanner for Drupal, WordPress, Joomla, Moodle, SilverStripe',
        'check_cmd': 'droopescan', 'install_apt': None, 'install_pip': 'droopescan',
        'usable_in': ['quick', 'advanced', 'ai'],
    },
    'joomscan': {
        'name': 'JoomScan', 'icon': '🔶', 'category': 'Joomla',
        'desc': 'OWASP Joomla vulnerability scanner',
        'check_cmd': 'joomscan', 'install_apt': 'joomscan', 'install_pip': None,
        'usable_in': ['quick', 'advanced', 'ai'],
    },

    # ─── Subdomain & Recon ─────────────────────────
    'subfinder': {
        'name': 'Subfinder', 'icon': '🌍', 'category': 'Subdomain',
        'desc': 'Subdomain discovery tool (ProjectDiscovery)',
        'check_cmd': 'subfinder', 'install_apt': None, 'install_pip': None,
        'install_custom': 'go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest',
        'usable_in': ['advanced', 'ai'],
    },
    'amass': {
        'name': 'Amass', 'icon': '🗺️', 'category': 'OSINT/Recon',
        'desc': 'In-depth attack surface mapping and discovery',
        'check_cmd': 'amass', 'install_apt': 'amass', 'install_pip': None,
        'usable_in': ['advanced', 'ai'],
    },
    'findomain': {
        'name': 'Findomain', 'icon': '🔎', 'category': 'Subdomain',
        'desc': 'Cross-platform subdomain enumerator (Rust)',
        'check_cmd': 'findomain', 'install_apt': None, 'install_pip': None,
        'install_custom': 'cargo install findomain',
        'usable_in': ['advanced', 'ai'],
    },
    'chaos': {
        'name': 'Chaos', 'icon': '🌀', 'category': 'Subdomain',
        'desc': 'ProjectDiscovery Chaos client for subdomain data',
        'check_cmd': 'chaos', 'install_apt': None, 'install_pip': None,
        'install_custom': 'go install -v github.com/projectdiscovery/chaos-client/cmd/chaos@latest',
        'usable_in': ['advanced', 'ai'],
    },
    'github_subdomains': {
        'name': 'github-subdomains', 'icon': '🐙', 'category': 'Subdomain',
        'desc': 'Find subdomains via GitHub source code search',
        'check_cmd': 'github-subdomains', 'install_apt': None, 'install_pip': None,
        'install_custom': 'go install github.com/gwen001/github-subdomains@latest',
        'usable_in': ['advanced', 'ai'],
    },
    'subjack': {
        'name': 'Subjack', 'icon': '🏴', 'category': 'Subdomain Takeover',
        'desc': 'Subdomain takeover vulnerability checker',
        'check_cmd': 'subjack', 'install_apt': None, 'install_pip': None,
        'install_custom': 'go install github.com/haccer/subjack@latest',
        'usable_in': ['quick', 'advanced', 'ai'],
    },
    'assetfinder': {
        'name': 'Assetfinder', 'icon': '🏷️', 'category': 'Subdomain',
        'desc': 'Find subdomains and related assets',
        'check_cmd': 'assetfinder', 'install_apt': None, 'install_pip': None,
        'install_custom': 'go install github.com/tomnomnom/assetfinder@latest',
        'usable_in': ['advanced', 'ai'],
    },

    # ─── HTTP Probing ──────────────────────────────
    'httpx_tool': {
        'name': 'httpx (PD)', 'icon': '🌐', 'category': 'HTTP Probe',
        'desc': 'Fast multi-purpose HTTP toolkit (ProjectDiscovery)',
        'check_cmd': 'httpx', 'install_apt': None, 'install_pip': None,
        'install_custom': 'go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest',
        'usable_in': ['quick', 'advanced', 'ai'],
    },
    'httprobe': {
        'name': 'httprobe', 'icon': '📡', 'category': 'HTTP Probe',
        'desc': 'Probe for working HTTP/HTTPS servers',
        'check_cmd': 'httprobe', 'install_apt': None, 'install_pip': None,
        'install_custom': 'go install github.com/tomnomnom/httprobe@latest',
        'usable_in': ['quick', 'advanced', 'ai'],
    },

    # ─── Vulnerability Scanning ────────────────────
    'nuclei': {
        'name': 'Nuclei', 'icon': '☢️', 'category': 'Vuln Scanner',
        'desc': 'Template-based vulnerability scanner (ProjectDiscovery)',
        'check_cmd': 'nuclei', 'install_apt': None, 'install_pip': None,
        'install_custom': 'go install -v github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest',
        'usable_in': ['quick', 'advanced', 'ai'],
    },
    'openvas': {
        'name': 'OpenVAS', 'icon': '🛡️', 'category': 'Vuln Scanner',
        'desc': 'Open Vulnerability Assessment System (full framework)',
        'check_cmd': 'gvm-cli', 'install_apt': 'openvas', 'install_pip': None,
        'usable_in': ['advanced'],
    },
    'interactsh_client': {
        'name': 'Interactsh', 'icon': '📨', 'category': 'OOB Testing',
        'desc': 'Out-of-band interaction gathering (ProjectDiscovery)',
        'check_cmd': 'interactsh-client', 'install_apt': None, 'install_pip': None,
        'install_custom': 'go install -v github.com/projectdiscovery/interactsh/cmd/interactsh-client@latest',
        'usable_in': ['advanced', 'ai'],
    },

    # ─── SSL/TLS ───────────────────────────────────
    'sslscan': {
        'name': 'SSLScan', 'icon': '🔒', 'category': 'SSL/TLS',
        'desc': 'Tests SSL/TLS enabled services for cipher suites',
        'check_cmd': 'sslscan', 'install_apt': 'sslscan', 'install_pip': None,
        'usable_in': ['quick', 'advanced', 'ai'],
    },
    'sslyze': {
        'name': 'SSLyze', 'icon': '🔑', 'category': 'SSL/TLS',
        'desc': 'Fast TLS/SSL scanner and configuration analyzer',
        'check_cmd': 'sslyze', 'install_apt': None, 'install_pip': 'sslyze',
        'usable_in': ['quick', 'advanced', 'ai'],
    },
    'testssl': {
        'name': 'testssl.sh', 'icon': '📜', 'category': 'SSL/TLS',
        'desc': 'Testing TLS/SSL encryption on any port',
        'check_cmd': 'testssl', 'install_apt': 'testssl.sh', 'install_pip': None,
        'usable_in': ['advanced', 'ai'],
    },

    # ─── Command Injection ─────────────────────────
    'commix': {
        'name': 'Commix', 'icon': '💉', 'category': 'Command Injection',
        'desc': 'Automated OS command injection testing',
        'check_cmd': 'commix', 'install_apt': None, 'install_pip': 'commix',
        'usable_in': ['advanced', 'ai'],
    },

    # ─── Parameter Discovery / URL Manipulation ────
    'paramspider': {
        'name': 'ParamSpider', 'icon': '🕷️', 'category': 'Param Discovery',
        'desc': 'Mining parameters from web archives for bug hunting',
        'check_cmd': 'paramspider', 'install_apt': None, 'install_pip': 'paramspider',
        'usable_in': ['quick', 'advanced', 'ai'],
    },
    'arjun': {
        'name': 'Arjun', 'icon': '🏹', 'category': 'Param Discovery',
        'desc': 'HTTP parameter discovery suite',
        'check_cmd': 'arjun', 'install_apt': None, 'install_pip': 'arjun',
        'usable_in': ['quick', 'advanced', 'ai'],
    },
    'qsreplace': {
        'name': 'qsreplace', 'icon': '🔁', 'category': 'URL Manipulation',
        'desc': 'Accept URLs on stdin, replace query string values',
        'check_cmd': 'qsreplace', 'install_apt': None, 'install_pip': None,
        'install_custom': 'go install github.com/tomnomnom/qsreplace@latest',
        'usable_in': ['advanced', 'ai'],
    },
    'unfurl': {
        'name': 'Unfurl', 'icon': '🔗', 'category': 'URL Manipulation',
        'desc': 'Pull out bits of URLs for analysis (domains, paths, params)',
        'check_cmd': 'unfurl', 'install_apt': None, 'install_pip': None,
        'install_custom': 'go install github.com/tomnomnom/unfurl@latest',
        'usable_in': ['advanced', 'ai'],
    },
    'gf': {
        'name': 'gf', 'icon': '🧲', 'category': 'Pattern Grep',
        'desc': 'Grep wrapper using pattern files (tomnomnom)',
        'check_cmd': 'gf', 'install_apt': None, 'install_pip': None,
        'install_custom': 'go install github.com/tomnomnom/gf@latest',
        'usable_in': ['advanced', 'ai'],
    },

    # ─── Web Proxy / Manual Testing ────────────────
    'burpsuite': {
        'name': 'Burp Suite', 'icon': '🔥', 'category': 'Web Proxy',
        'desc': 'Web vulnerability scanner and proxy (PortSwigger)',
        'check_cmd': 'burpsuite', 'install_apt': None, 'install_pip': None,
        'install_custom': 'echo "Download from https://portswigger.net/burp/releases"',
        'usable_in': ['advanced'],
    },
    'owasp_zap': {
        'name': 'OWASP ZAP', 'icon': '⚡', 'category': 'Web Proxy',
        'desc': 'Zed Attack Proxy — OWASP web app security scanner',
        'check_cmd': 'zap-cli', 'install_apt': None, 'install_pip': 'zaproxy',
        'usable_in': ['quick', 'advanced', 'ai'],
    },
    'mitmproxy': {
        'name': 'mitmproxy', 'icon': '🔀', 'category': 'Web Proxy',
        'desc': 'Interactive TLS-capable intercepting HTTP proxy',
        'check_cmd': 'mitmproxy', 'install_apt': None, 'install_pip': 'mitmproxy',
        'usable_in': ['advanced'],
    },

    # ─── API Testing ──────────────────────────────
    'newman': {
        'name': 'Newman', 'icon': '📬', 'category': 'API Testing',
        'desc': 'Postman collection runner (CLI)',
        'check_cmd': 'newman', 'install_apt': None, 'install_pip': None,
        'install_custom': 'npm install -g newman',
        'usable_in': ['quick', 'advanced', 'ai'],
    },
    'kiterunner': {
        'name': 'Kiterunner', 'icon': '🪁', 'category': 'API Testing',
        'desc': 'API endpoint discovery and content scanner',
        'check_cmd': 'kr', 'install_apt': None, 'install_pip': None,
        'install_custom': 'go install github.com/assetnote/kiterunner/cmd/kr@latest',
        'usable_in': ['advanced', 'ai'],
    },

    # ─── Web Recon / URL Collection ───────────────
    'waybackurls': {
        'name': 'Waybackurls', 'icon': '⏪', 'category': 'Web Recon',
        'desc': 'Fetch all URLs from Wayback Machine',
        'check_cmd': 'waybackurls', 'install_apt': None, 'install_pip': None,
        'install_custom': 'go install github.com/tomnomnom/waybackurls@latest',
        'usable_in': ['quick', 'advanced', 'ai'],
    },
    'gau': {
        'name': 'gau', 'icon': '🔗', 'category': 'Web Recon',
        'desc': 'Get All URLs from AlienVault, Wayback, Common Crawl',
        'check_cmd': 'gau', 'install_apt': None, 'install_pip': None,
        'install_custom': 'go install github.com/lc/gau/v2/cmd/gau@latest',
        'usable_in': ['quick', 'advanced', 'ai'],
    },
    'hakrawler': {
        'name': 'Hakrawler', 'icon': '🕷️', 'category': 'Web Recon',
        'desc': 'Fast web crawler for gathering URLs and JS file locations',
        'check_cmd': 'hakrawler', 'install_apt': None, 'install_pip': None,
        'install_custom': 'go install github.com/hakluke/hakrawler@latest',
        'usable_in': ['quick', 'advanced', 'ai'],
    },
    'katana': {
        'name': 'Katana', 'icon': '⚔️', 'category': 'Web Recon',
        'desc': 'Next-gen crawling and spidering framework (PD)',
        'check_cmd': 'katana', 'install_apt': None, 'install_pip': None,
        'install_custom': 'go install github.com/projectdiscovery/katana/cmd/katana@latest',
        'usable_in': ['quick', 'advanced', 'ai'],
    },

    # ─── Screenshot / Visual Recon ────────────────
    'aquatone': {
        'name': 'Aquatone', 'icon': '📸', 'category': 'Visual Recon',
        'desc': 'Visual inspection of websites across large attack surfaces',
        'check_cmd': 'aquatone', 'install_apt': None, 'install_pip': None,
        'install_custom': 'go install github.com/michenriksen/aquatone@latest',
        'usable_in': ['advanced', 'ai'],
    },
    'gowitness': {
        'name': 'Gowitness', 'icon': '📷', 'category': 'Visual Recon',
        'desc': 'Website screenshot tool using Chrome headless',
        'check_cmd': 'gowitness', 'install_apt': None, 'install_pip': None,
        'install_custom': 'go install github.com/sensepost/gowitness@latest',
        'usable_in': ['advanced', 'ai'],
    },

    # ─── DNS Recon ────────────────────────────────
    'dnsx': {
        'name': 'dnsx', 'icon': '🌐', 'category': 'DNS Recon',
        'desc': 'Fast multi-purpose DNS toolkit (ProjectDiscovery)',
        'check_cmd': 'dnsx', 'install_apt': None, 'install_pip': None,
        'install_custom': 'go install -v github.com/projectdiscovery/dnsx/cmd/dnsx@latest',
        'usable_in': ['advanced', 'ai'],
    },
    'shuffledns': {
        'name': 'ShuffleDNS', 'icon': '🔀', 'category': 'DNS Recon',
        'desc': 'Wrapper around massdns for active DNS brute-forcing',
        'check_cmd': 'shuffledns', 'install_apt': None, 'install_pip': None,
        'install_custom': 'go install -v github.com/projectdiscovery/shuffledns/cmd/shuffledns@latest',
        'usable_in': ['advanced', 'ai'],
    },

    # ─── Static Analysis / SAST ───────────────────
    'semgrep': {
        'name': 'Semgrep', 'icon': '🔎', 'category': 'SAST',
        'desc': 'Lightweight static analysis for many languages',
        'check_cmd': 'semgrep', 'install_apt': None, 'install_pip': 'semgrep',
        'usable_in': ['advanced', 'ai'],
    },
    'bandit': {
        'name': 'Bandit', 'icon': '🐍', 'category': 'SAST',
        'desc': 'Python source code security analyzer',
        'check_cmd': 'bandit', 'install_apt': None, 'install_pip': 'bandit',
        'usable_in': ['quick', 'advanced', 'ai'],
    },
    'brakeman': {
        'name': 'Brakeman', 'icon': '💎', 'category': 'SAST',
        'desc': 'Static analysis security scanner for Ruby on Rails',
        'check_cmd': 'brakeman', 'install_apt': None, 'install_pip': None,
        'install_custom': 'gem install brakeman',
        'usable_in': ['advanced'],
    },

    # ─── Secret Scanning ─────────────────────────
    'gitleaks': {
        'name': 'Gitleaks', 'icon': '🔐', 'category': 'Secret Scanner',
        'desc': 'Scan git repos for secrets and sensitive data',
        'check_cmd': 'gitleaks', 'install_apt': None, 'install_pip': None,
        'install_custom': 'go install github.com/gitleaks/gitleaks/v8@latest',
        'usable_in': ['quick', 'advanced', 'ai'],
    },
    'trufflehog': {
        'name': 'TruffleHog', 'icon': '🐷', 'category': 'Secret Scanner',
        'desc': 'Find credentials in git repositories',
        'check_cmd': 'trufflehog', 'install_apt': None, 'install_pip': 'trufflehog',
        'usable_in': ['quick', 'advanced', 'ai'],
    },
    'detect_secrets': {
        'name': 'detect-secrets', 'icon': '🕵️', 'category': 'Secret Scanner',
        'desc': 'Enterprise-friendly secret detection in code',
        'check_cmd': 'detect-secrets', 'install_apt': None, 'install_pip': 'detect-secrets',
        'usable_in': ['quick', 'advanced', 'ai'],
    },

    # ─── Wordlists ────────────────────────────────
    'seclists': {
        'name': 'SecLists', 'icon': '📚', 'category': 'Wordlists',
        'desc': 'Collection of wordlists for fuzzing and discovery',
        'check_cmd': None, 'install_apt': 'seclists', 'install_pip': None,
        'install_custom': 'git clone --depth 1 https://github.com/danielmiessler/SecLists.git /usr/share/seclists',
        'usable_in': ['advanced', 'ai'],
    },

    # ─── Exploitation ──────────────────────────────
    'searchsploit': {
        'name': 'SearchSploit', 'icon': '🔍', 'category': 'Exploit DB',
        'desc': 'CLI search tool for Exploit Database',
        'check_cmd': 'searchsploit', 'install_apt': 'exploitdb', 'install_pip': None,
        'usable_in': ['advanced', 'ai'],
    },

    # ─── Python Libraries ──────────────────────────
    'aiohttp': {
        'name': 'aiohttp', 'icon': '📡', 'category': 'Python HTTP',
        'desc': 'Async HTTP client/server for Python',
        'check_cmd': None, 'install_apt': None, 'install_pip': 'aiohttp',
        'usable_in': ['quick', 'advanced', 'ai'],
    },
    'httpx_pkg': {
        'name': 'httpx (Python)', 'icon': '🔗', 'category': 'Python HTTP',
        'desc': 'Modern HTTP client with HTTP/2 support',
        'check_cmd': None, 'install_apt': None, 'install_pip': 'httpx',
        'usable_in': ['quick', 'advanced', 'ai'],
    },
    'requests': {
        'name': 'Requests', 'icon': '📨', 'category': 'Python HTTP',
        'desc': 'Simple HTTP library for Python',
        'check_cmd': None, 'install_apt': None, 'install_pip': 'requests',
        'usable_in': ['quick', 'advanced', 'ai'],
    },
    'beautifulsoup': {
        'name': 'BeautifulSoup', 'icon': '🍲', 'category': 'HTML Parser',
        'desc': 'HTML/XML parser for web scraping',
        'check_cmd': None, 'install_apt': None, 'install_pip': 'beautifulsoup4',
        'usable_in': ['quick', 'advanced', 'ai'],
    },
    'scrapy': {
        'name': 'Scrapy', 'icon': '🕸️', 'category': 'Web Crawler',
        'desc': 'Fast high-level web crawling framework',
        'check_cmd': 'scrapy', 'install_apt': None, 'install_pip': 'scrapy',
        'usable_in': ['advanced', 'ai'],
    },

    # ─── AI / LLM SDK ─────────────────────────────
    'google_genai': {
        'name': 'Google GenAI', 'icon': '🤖', 'category': 'AI/LLM SDK',
        'desc': 'Google Gemini AI SDK for Python',
        'check_cmd': None, 'install_apt': None, 'install_pip': 'google-genai',
        'usable_in': ['ai'],
    },
    'openai_sdk': {
        'name': 'OpenAI SDK', 'icon': '🧠', 'category': 'AI/LLM SDK',
        'desc': 'OpenAI GPT API client library',
        'check_cmd': None, 'install_apt': None, 'install_pip': 'openai',
        'usable_in': ['ai'],
    },
    'anthropic_sdk': {
        'name': 'Anthropic SDK', 'icon': '🔬', 'category': 'AI/LLM SDK',
        'desc': 'Anthropic Claude API client library',
        'check_cmd': None, 'install_apt': None, 'install_pip': 'anthropic',
        'usable_in': ['ai'],
    },

    # ─── Reporting / Management ──────────────────
    'dradis': {
        'name': 'Dradis', 'icon': '📝', 'category': 'Reporting',
        'desc': 'Collaboration and reporting platform for pentesters',
        'check_cmd': 'dradis', 'install_apt': None, 'install_pip': None,
        'install_custom': 'gem install dradis',
        'usable_in': ['advanced'],
    },
    'faraday': {
        'name': 'Faraday', 'icon': '🏭', 'category': 'Reporting',
        'desc': 'Collaborative vulnerability management platform',
        'check_cmd': 'faraday-cli', 'install_apt': None, 'install_pip': 'faraday-cli',
        'usable_in': ['advanced'],
    },
    'defectdojo': {
        'name': 'DefectDojo', 'icon': '🥋', 'category': 'Reporting',
        'desc': 'DevSecOps vulnerability management and correlation',
        'check_cmd': None, 'install_apt': None, 'install_pip': None,
        'install_custom': 'echo "Deploy via Docker: https://github.com/DefectDojo/django-DefectDojo"',
        'usable_in': ['advanced'],
    },
}

# Filtered helpers
def get_tools_for_tab(tab_name):
    """Get tools available for a specific tab (quick, advanced, ai)"""
    return {k: v for k, v in SECURITY_TOOLS.items() if tab_name in v.get('usable_in', [])}

def get_categories():
    """Get unique tool categories"""
    return sorted(set(info['category'] for info in SECURITY_TOOLS.values()))

def get_tools_by_category(category, tab_name=None):
    """Get tools filtered by category and optional tab"""
    result = {}
    for k, v in SECURITY_TOOLS.items():
        if v['category'] == category:
            if tab_name is None or tab_name in v.get('usable_in', []):
                result[k] = v
    return result

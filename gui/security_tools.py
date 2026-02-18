"""
security_tools.py — Shared cybersecurity tools registry for EMYUEL

Central registry of all supported security tools with install/detect metadata.
Used by AI Analysis, Quick Scan, and Advanced Scan tabs.
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
    'httpx_tool': {
        'name': 'httpx (PD)', 'icon': '🌐', 'category': 'HTTP Probe',
        'desc': 'Fast multi-purpose HTTP toolkit (ProjectDiscovery)',
        'check_cmd': 'httpx', 'install_apt': None, 'install_pip': None,
        'install_custom': 'go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest',
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

    # ─── Exploitation ──────────────────────────────
    'metasploit': {
        'name': 'Metasploit', 'icon': '💀', 'category': 'Exploitation',
        'desc': 'Penetration testing framework with exploit modules',
        'check_cmd': 'msfconsole', 'install_apt': None, 'install_pip': None,
        'install_custom': 'curl https://raw.githubusercontent.com/rapid7/metasploit-omnibus/master/config/templates/metasploit-framework-wrappers/msfupdate.erb > msfinstall && chmod 755 msfinstall && ./msfinstall',
        'usable_in': ['advanced'],
    },
    'commix': {
        'name': 'Commix', 'icon': '💉', 'category': 'Command Injection',
        'desc': 'Automated OS command injection testing',
        'check_cmd': 'commix', 'install_apt': None, 'install_pip': 'commix',
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

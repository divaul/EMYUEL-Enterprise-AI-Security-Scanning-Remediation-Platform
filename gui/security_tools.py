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

    # ─── Network Sniffing / Traffic Analysis ───────
    'wireshark': {
        'name': 'Wireshark', 'icon': '🦈', 'category': 'Traffic Analysis',
        'desc': 'Network protocol analyzer with GUI',
        'check_cmd': 'wireshark', 'install_apt': 'wireshark', 'install_pip': None,
        'usable_in': ['advanced'],
    },
    'tcpdump': {
        'name': 'tcpdump', 'icon': '📡', 'category': 'Traffic Analysis',
        'desc': 'Command-line packet analyzer',
        'check_cmd': 'tcpdump', 'install_apt': 'tcpdump', 'install_pip': None,
        'usable_in': ['advanced'],
    },
    'tshark': {
        'name': 'TShark', 'icon': '🦈', 'category': 'Traffic Analysis',
        'desc': 'Terminal-based Wireshark (CLI packet analyzer)',
        'check_cmd': 'tshark', 'install_apt': 'tshark', 'install_pip': None,
        'usable_in': ['advanced', 'ai'],
    },
    'ettercap': {
        'name': 'Ettercap', 'icon': '🕵️', 'category': 'MITM',
        'desc': 'Comprehensive suite for man-in-the-middle attacks',
        'check_cmd': 'ettercap', 'install_apt': 'ettercap-text-only', 'install_pip': None,
        'usable_in': ['advanced'],
    },
    'bettercap': {
        'name': 'Bettercap', 'icon': '🎩', 'category': 'MITM',
        'desc': 'Swiss army knife for WiFi, BLE, and network attacks',
        'check_cmd': 'bettercap', 'install_apt': 'bettercap', 'install_pip': None,
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
    'arjun': {
        'name': 'Arjun', 'icon': '🏹', 'category': 'API Testing',
        'desc': 'HTTP parameter discovery suite',
        'check_cmd': 'arjun', 'install_apt': None, 'install_pip': 'arjun',
        'usable_in': ['quick', 'advanced', 'ai'],
    },

    # ─── Cloud Security ───────────────────────────
    'prowler': {
        'name': 'Prowler', 'icon': '🦁', 'category': 'Cloud Security',
        'desc': 'AWS/Azure/GCP security best practices assessment',
        'check_cmd': 'prowler', 'install_apt': None, 'install_pip': 'prowler',
        'usable_in': ['advanced', 'ai'],
    },
    'scoutsuite': {
        'name': 'ScoutSuite', 'icon': '🔭', 'category': 'Cloud Security',
        'desc': 'Multi-cloud security auditing tool',
        'check_cmd': 'scout', 'install_apt': None, 'install_pip': 'scoutsuite',
        'usable_in': ['advanced', 'ai'],
    },
    'cloudmapper': {
        'name': 'CloudMapper', 'icon': '☁️', 'category': 'Cloud Security',
        'desc': 'AWS environment analysis and visualization',
        'check_cmd': None, 'install_apt': None, 'install_pip': 'cloudmapper',
        'usable_in': ['advanced'],
    },
    'pacu': {
        'name': 'Pacu', 'icon': '🐟', 'category': 'Cloud Security',
        'desc': 'AWS exploitation framework (Rhino Security)',
        'check_cmd': 'pacu', 'install_apt': None, 'install_pip': 'pacu',
        'usable_in': ['advanced'],
    },
    'kube_hunter': {
        'name': 'kube-hunter', 'icon': '🎯', 'category': 'K8s Security',
        'desc': 'Kubernetes penetration testing tool',
        'check_cmd': 'kube-hunter', 'install_apt': None, 'install_pip': 'kube-hunter',
        'usable_in': ['advanced', 'ai'],
    },
    'kube_bench': {
        'name': 'kube-bench', 'icon': '📋', 'category': 'K8s Security',
        'desc': 'CIS Kubernetes Benchmark checker',
        'check_cmd': 'kube-bench', 'install_apt': None, 'install_pip': None,
        'install_custom': 'go install github.com/aquasecurity/kube-bench@latest',
        'usable_in': ['advanced', 'ai'],
    },
    'trivy': {
        'name': 'Trivy', 'icon': '🔺', 'category': 'Container Security',
        'desc': 'Comprehensive vulnerability scanner for containers/IaC',
        'check_cmd': 'trivy', 'install_apt': None, 'install_pip': None,
        'install_custom': 'curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b /usr/local/bin',
        'usable_in': ['quick', 'advanced', 'ai'],
    },
    'grype': {
        'name': 'Grype', 'icon': '🦅', 'category': 'Container Security',
        'desc': 'Vulnerability scanner for container images and filesystems',
        'check_cmd': 'grype', 'install_apt': None, 'install_pip': None,
        'install_custom': 'curl -sSfL https://raw.githubusercontent.com/anchore/grype/main/install.sh | sh -s -- -b /usr/local/bin',
        'usable_in': ['advanced', 'ai'],
    },

    # ─── Container / DevSecOps ────────────────────
    'dockle': {
        'name': 'Dockle', 'icon': '🐳', 'category': 'Container Security',
        'desc': 'Container image linter for security best practices',
        'check_cmd': 'dockle', 'install_apt': None, 'install_pip': None,
        'install_custom': 'go install github.com/goodwithtech/dockle/cmd/dockle@latest',
        'usable_in': ['advanced'],
    },
    'clair': {
        'name': 'Clair', 'icon': '🔬', 'category': 'Container Security',
        'desc': 'Static analysis of vulnerabilities in container images',
        'check_cmd': 'clair', 'install_apt': None, 'install_pip': None,
        'install_custom': 'go install github.com/quay/clair/v4/cmd/clair@latest',
        'usable_in': ['advanced'],
    },
    'anchore_cli': {
        'name': 'Anchore CLI', 'icon': '⚓', 'category': 'Container Security',
        'desc': 'Anchore Engine CLI for container image analysis',
        'check_cmd': 'anchore-cli', 'install_apt': None, 'install_pip': 'anchorecli',
        'usable_in': ['advanced'],
    },
    'checkov': {
        'name': 'Checkov', 'icon': '✅', 'category': 'IaC Security',
        'desc': 'Static analysis for infrastructure-as-code (Terraform, K8s, etc.)',
        'check_cmd': 'checkov', 'install_apt': None, 'install_pip': 'checkov',
        'usable_in': ['advanced', 'ai'],
    },
    'tfsec': {
        'name': 'tfsec', 'icon': '🏗️', 'category': 'IaC Security',
        'desc': 'Security scanner for Terraform code',
        'check_cmd': 'tfsec', 'install_apt': None, 'install_pip': None,
        'install_custom': 'go install github.com/aquasecurity/tfsec/cmd/tfsec@latest',
        'usable_in': ['advanced', 'ai'],
    },
    'terrascan': {
        'name': 'Terrascan', 'icon': '🌍', 'category': 'IaC Security',
        'desc': 'Detect compliance and security violations in IaC',
        'check_cmd': 'terrascan', 'install_apt': None, 'install_pip': None,
        'install_custom': 'go install github.com/tenable/terrascan/cmd/terrascan@latest',
        'usable_in': ['advanced'],
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
    'spotbugs': {
        'name': 'SpotBugs', 'icon': '🐛', 'category': 'SAST',
        'desc': 'Static analysis tool for finding Java bugs',
        'check_cmd': 'spotbugs', 'install_apt': None, 'install_pip': None,
        'install_custom': 'echo "Download from https://spotbugs.github.io/"',
        'usable_in': ['advanced'],
    },
    'sonarscanner': {
        'name': 'SonarScanner', 'icon': '📊', 'category': 'SAST',
        'desc': 'SonarQube scanner for continuous code quality',
        'check_cmd': 'sonar-scanner', 'install_apt': None, 'install_pip': None,
        'install_custom': 'echo "Download from https://docs.sonarqube.org/latest/analysis/scan/sonarscanner/"',
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

    # ─── Binary / Reverse Engineering ─────────────
    'ghidra': {
        'name': 'Ghidra', 'icon': '🐉', 'category': 'Reverse Engineering',
        'desc': 'NSA software reverse engineering framework',
        'check_cmd': 'ghidra', 'install_apt': None, 'install_pip': None,
        'install_custom': 'echo "Download from https://ghidra-sre.org/"',
        'usable_in': ['advanced'],
    },
    'radare2': {
        'name': 'Radare2', 'icon': '🔧', 'category': 'Reverse Engineering',
        'desc': 'Open-source RE framework with disassembler',
        'check_cmd': 'r2', 'install_apt': 'radare2', 'install_pip': None,
        'usable_in': ['advanced'],
    },
    'cutter': {
        'name': 'Cutter', 'icon': '✂️', 'category': 'Reverse Engineering',
        'desc': 'GUI for Radare2 reverse engineering',
        'check_cmd': 'cutter', 'install_apt': None, 'install_pip': None,
        'install_custom': 'echo "Download from https://cutter.re/"',
        'usable_in': ['advanced'],
    },
    'apktool': {
        'name': 'APKTool', 'icon': '📱', 'category': 'Mobile Security',
        'desc': 'Reverse engineering tool for Android APKs',
        'check_cmd': 'apktool', 'install_apt': 'apktool', 'install_pip': None,
        'usable_in': ['advanced'],
    },
    'jadx': {
        'name': 'JADX', 'icon': '☕', 'category': 'Mobile Security',
        'desc': 'DEX to Java decompiler for Android',
        'check_cmd': 'jadx', 'install_apt': None, 'install_pip': None,
        'install_custom': 'echo "Download from https://github.com/skylot/jadx/releases"',
        'usable_in': ['advanced'],
    },

    # ─── Forensics ────────────────────────────────
    'volatility3': {
        'name': 'Volatility 3', 'icon': '🧪', 'category': 'Forensics',
        'desc': 'Advanced memory forensics framework',
        'check_cmd': 'vol', 'install_apt': None, 'install_pip': 'volatility3',
        'usable_in': ['advanced'],
    },
    'autopsy': {
        'name': 'Autopsy', 'icon': '🔍', 'category': 'Forensics',
        'desc': 'Digital forensics platform (GUI)',
        'check_cmd': 'autopsy', 'install_apt': 'autopsy', 'install_pip': None,
        'usable_in': ['advanced'],
    },
    'binwalk': {
        'name': 'Binwalk', 'icon': '📦', 'category': 'Forensics',
        'desc': 'Firmware analysis and extraction tool',
        'check_cmd': 'binwalk', 'install_apt': 'binwalk', 'install_pip': None,
        'usable_in': ['advanced'],
    },
    'foremost': {
        'name': 'Foremost', 'icon': '🗃️', 'category': 'Forensics',
        'desc': 'File carving tool for data recovery',
        'check_cmd': 'foremost', 'install_apt': 'foremost', 'install_pip': None,
        'usable_in': ['advanced'],
    },

    # ─── Wireless / WiFi ─────────────────────────
    'aircrack_ng': {
        'name': 'Aircrack-ng', 'icon': '📶', 'category': 'Wireless',
        'desc': 'WiFi network security assessment suite',
        'check_cmd': 'aircrack-ng', 'install_apt': 'aircrack-ng', 'install_pip': None,
        'usable_in': ['advanced'],
    },
    'kismet': {
        'name': 'Kismet', 'icon': '📡', 'category': 'Wireless',
        'desc': 'Wireless network and device detector/sniffer',
        'check_cmd': 'kismet', 'install_apt': 'kismet', 'install_pip': None,
        'usable_in': ['advanced'],
    },
    'reaver': {
        'name': 'Reaver', 'icon': '🔓', 'category': 'Wireless',
        'desc': 'WPS brute-force attack tool',
        'check_cmd': 'reaver', 'install_apt': 'reaver', 'install_pip': None,
        'usable_in': ['advanced'],
    },
    'wifite': {
        'name': 'Wifite', 'icon': '📻', 'category': 'Wireless',
        'desc': 'Automated wireless network auditing',
        'check_cmd': 'wifite', 'install_apt': 'wifite', 'install_pip': None,
        'usable_in': ['advanced'],
    },

    # ─── Social Engineering ──────────────────────
    'gophish': {
        'name': 'GoPhish', 'icon': '🎣', 'category': 'Social Engineering',
        'desc': 'Open-source phishing framework',
        'check_cmd': 'gophish', 'install_apt': None, 'install_pip': None,
        'install_custom': 'go install github.com/gophish/gophish@latest',
        'usable_in': ['advanced'],
    },
    'setoolkit': {
        'name': 'SET', 'icon': '🎭', 'category': 'Social Engineering',
        'desc': 'Social-Engineer Toolkit by TrustedSec',
        'check_cmd': 'setoolkit', 'install_apt': None, 'install_pip': None,
        'install_custom': 'git clone https://github.com/trustedsec/social-engineer-toolkit.git /opt/set && cd /opt/set && pip install -r requirements.txt',
        'usable_in': ['advanced'],
    },
    'king_phisher': {
        'name': 'King Phisher', 'icon': '👑', 'category': 'Social Engineering',
        'desc': 'Phishing campaign toolkit with server/client',
        'check_cmd': 'king-phisher', 'install_apt': None, 'install_pip': None,
        'install_custom': 'echo "Visit https://github.com/rsmusllp/king-phisher"',
        'usable_in': ['advanced'],
    },

    # ─── Additional Web Recon ────────────────────
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
    'dnsx': {
        'name': 'dnsx', 'icon': '🌐', 'category': 'DNS Recon',
        'desc': 'Fast multi-purpose DNS toolkit (ProjectDiscovery)',
        'check_cmd': 'dnsx', 'install_apt': None, 'install_pip': None,
        'install_custom': 'go install -v github.com/projectdiscovery/dnsx/cmd/dnsx@latest',
        'usable_in': ['advanced', 'ai'],
    },
    'assetfinder': {
        'name': 'Assetfinder', 'icon': '🏷️', 'category': 'Subdomain',
        'desc': 'Find subdomains and related assets',
        'check_cmd': 'assetfinder', 'install_apt': None, 'install_pip': None,
        'install_custom': 'go install github.com/tomnomnom/assetfinder@latest',
        'usable_in': ['advanced', 'ai'],
    },
    'shuffledns': {
        'name': 'ShuffleDNS', 'icon': '🔀', 'category': 'DNS Recon',
        'desc': 'Wrapper around massdns for active DNS brute-forcing',
        'check_cmd': 'shuffledns', 'install_apt': None, 'install_pip': None,
        'install_custom': 'go install -v github.com/projectdiscovery/shuffledns/cmd/shuffledns@latest',
        'usable_in': ['advanced', 'ai'],
    },

    # ─── Infrastructure / Service Enumeration ─────
    'enum4linux_ng': {
        'name': 'enum4linux-ng', 'icon': '🐧', 'category': 'Enumeration',
        'desc': 'Next-gen Linux/Samba enumeration tool',
        'check_cmd': 'enum4linux-ng', 'install_apt': None, 'install_pip': 'enum4linux-ng',
        'usable_in': ['advanced', 'ai'],
    },
    'smbclient': {
        'name': 'smbclient', 'icon': '📁', 'category': 'Enumeration',
        'desc': 'SMB/CIFS client for accessing Windows shares',
        'check_cmd': 'smbclient', 'install_apt': 'smbclient', 'install_pip': None,
        'usable_in': ['advanced'],
    },
    'crackmapexec': {
        'name': 'CrackMapExec', 'icon': '💀', 'category': 'Enumeration',
        'desc': 'Swiss army knife for pentesting Windows/AD environments',
        'check_cmd': 'crackmapexec', 'install_apt': None, 'install_pip': 'crackmapexec',
        'usable_in': ['advanced', 'ai'],
    },
    'ldapsearch': {
        'name': 'ldapsearch', 'icon': '📒', 'category': 'Enumeration',
        'desc': 'LDAP directory search and enumeration tool',
        'check_cmd': 'ldapsearch', 'install_apt': 'ldap-utils', 'install_pip': None,
        'usable_in': ['advanced'],
    },
    'snmpwalk': {
        'name': 'snmpwalk', 'icon': '🚶', 'category': 'Enumeration',
        'desc': 'SNMP MIB tree walker for network device enumeration',
        'check_cmd': 'snmpwalk', 'install_apt': 'snmp', 'install_pip': None,
        'usable_in': ['advanced'],
    },

    # ─── Exploitation / Post-Exploitation ─────────
    'empire': {
        'name': 'Empire', 'icon': '👑', 'category': 'Post-Exploitation',
        'desc': 'PowerShell and Python post-exploitation framework',
        'check_cmd': 'empire', 'install_apt': None, 'install_pip': None,
        'install_custom': 'pip install powershell-empire',
        'usable_in': ['advanced'],
    },
    'sliver': {
        'name': 'Sliver', 'icon': '🐍', 'category': 'C2 Framework',
        'desc': 'Open-source cross-platform adversary emulation/C2',
        'check_cmd': 'sliver', 'install_apt': None, 'install_pip': None,
        'install_custom': 'curl https://sliver.sh/install | sudo bash',
        'usable_in': ['advanced'],
    },
    'beef': {
        'name': 'BeEF', 'icon': '🥩', 'category': 'Browser Exploit',
        'desc': 'Browser Exploitation Framework for XSS testing',
        'check_cmd': 'beef-xss', 'install_apt': 'beef-xss', 'install_pip': None,
        'usable_in': ['advanced'],
    },
    'searchsploit': {
        'name': 'SearchSploit', 'icon': '🔍', 'category': 'Exploit DB',
        'desc': 'CLI search tool for Exploit Database',
        'check_cmd': 'searchsploit', 'install_apt': 'exploitdb', 'install_pip': None,
        'usable_in': ['advanced', 'ai'],
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

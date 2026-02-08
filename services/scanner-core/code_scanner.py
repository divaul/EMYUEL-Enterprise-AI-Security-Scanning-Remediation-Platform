"""
Code Scanner - Scan source code directories for vulnerabilities

Handles file traversal, code parsing, and static analysis
"""

import asyncio
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
import ast


class CodeScanner:
    """Scanner for source code directories"""
    
    def __init__(self, llm_analyzer):
        """
        Initialize code scanner
        
        Args:
            llm_analyzer: LLM analyzer instance
        """
        self.llm = llm_analyzer
    
    async def scan_directory(self, directory: str, modules: List[str] = None) -> List[Dict[str, Any]]:
        """
        Scan directory for vulnerabilities
        
        Args:
            directory: Directory path to scan
            modules: Vulnerability modules to check
            
        Returns:
            List of vulnerability findings
        """
        if modules is None or 'all' in modules:
            modules = ['secrets', 'sqli', 'xss', 'rce', 'path_traversal', 'crypto']
        
        all_findings = []
        
        # Find all source files
        print(f"[Code] Scanning directory: {directory}")
        files = self._find_source_files(directory)
        print(f"[Code] Found {len(files)} files to analyze")
        
        # Scan each file
        for i, file_path in enumerate(files):
            print(f"[Code] Analyzing file {i+1}/{len(files)}: {file_path.name}")
            
            file_findings = await self._scan_file(file_path, modules)
            all_findings.extend(file_findings)
        
        print(f"[Code] Scan complete: {len(all_findings)} vulnerabilities found")
        return all_findings
    
    def _find_source_files(self, directory: str) -> List[Path]:
        """Find all source code files in directory"""
        path = Path(directory)
        
        # Supported file extensions
        extensions = {'.py', '.js', '.ts', '.java', '.php', '.rb', '.go', '.cs', '.cpp', '.c', '.html', '.jsx', '.tsx', '.vue'}
        
        # Directories to exclude
        exclude_dirs = {'node_modules', '.git', '__pycache__', 'venv', 'env', 'dist', 'build', '.next', 'target'}
        
        files = []
        
        for file_path in path.rglob('*'):
            # Skip directories
            if file_path.is_dir():
                continue
            
            # Skip excluded directories
            if any(excluded in file_path.parts for excluded in exclude_dirs):
                continue
            
            # Check extension
            if file_path.suffix in extensions:
                files.append(file_path)
        
        return files
    
    async def _scan_file(self, file_path: Path, modules: List[str]) -> List[Dict[str, Any]]:
        """Scan individual file for vulnerabilities"""
        findings = []
        
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
        except Exception as e:
            print(f"[Code] Error reading {file_path}: {e}")
            return findings
        
        # Skip empty or very short files
        if len(content.strip()) < 20:
            return findings
        
        # Detect language
        language = self._detect_language(file_path.suffix)
        
        # 1. Check for hardcoded secrets
        if 'secrets' in modules:
            secret_findings = self._find_hardcoded_secrets(content, str(file_path))
            findings.extend(secret_findings)
        
        # 2. Static pattern matching for common vulnerabilities
        if language == 'python':
            pattern_findings = self._scan_python_patterns(content, str(file_path), modules)
            findings.extend(pattern_findings)
        elif language in ['javascript', 'typescript']:
            pattern_findings = self._scan_javascript_patterns(content, str(file_path), modules)
            findings.extend(pattern_findings)
        
        # 3. LLM analysis (for deeper inspection)
        # Only analyze files that are not too large
        if len(content) < 10000:
            llm_findings = await self.llm.analyze_code(content, str(file_path), language)
            findings.extend(llm_findings)
        
        return findings
    
    def _detect_language(self, extension: str) -> str:
        """Detect programming language from extension"""
        lang_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.jsx': 'javascript',
            '.tsx': 'typescript',
            '.java': 'java',
            '.php': 'php',
            '.rb': 'ruby',
            '.go': 'go',
            '.cs': 'csharp',
            '.cpp': 'cpp',
            '.c': 'c',
            '.html': 'html',
            '.vue': 'vue'
        }
        return lang_map.get(extension, 'unknown')
    
    def _find_hardcoded_secrets(self, content: str, file_path: str) -> List[Dict[str, Any]]:
        """Find hardcoded API keys, passwords, tokens"""
        findings = []
        
        # Patterns for common secrets
        secret_patterns = {
            'aws_key': r'AKIA[0-9A-Z]{16}',
            'generic_api_key': r'["\']?api[_-]?key["\']?\s*[:=]\s*["\']([a-zA-Z0-9_\-]{20,})["\']',
            'generic_secret': r'["\']?secret["\']?\s*[:=]\s*["\']([a-zA-Z0-9_\-]{16,})["\']',
            'password': r'["\']?password["\']?\s*[:=]\s*["\']([^"\']{6,})["\']',
            'private_key': r'-----BEGIN (RSA |EC |DSA )?PRIVATE KEY-----',
            'github_token': r'ghp_[a-zA-Z0-9]{36}',
            'google_api': r'AIza[0-9A-Za-z\\-_]{35}',
            'slack_token': r'xox[baprs]-[0-9a-zA-Z]{10,48}',
        }
        
        lines = content.split('\n')
        
        for pattern_name, pattern in secret_patterns.items():
            for line_num, line in enumerate(lines, 1):
                matches = re.finditer(pattern, line, re.IGNORECASE)
                
                for match in matches:
                    # Skip if it looks like a placeholder or example
                    if any(placeholder in line.lower() for placeholder in ['example', 'placeholder', 'your_', 'xxx', '...', 'todo']):
                        continue
                    
                    findings.append({
                        'type': 'hardcoded_secret',
                        'severity': 'critical',
                        'file': file_path,
                        'line': line_num,
                        'description': f'Hardcoded {pattern_name} detected',
                        'evidence': line.strip()[:100],
                        'remediation': 'Move secrets to environment variables or secure vault',
                        'source': 'static',
                        'confidence': 0.9
                    })
        
        return findings
    
    def _scan_python_patterns(self, content: str, file_path: str, modules: List[str]) -> List[Dict[str, Any]]:
        """Scan Python code for vulnerability patterns"""
        findings = []
        lines = content.split('\n')
        
        # SQL Injection patterns
        if 'sqli' in modules:
            sqli_patterns = [
                r'execute\s*\(\s*["\'].*%s.*["\']',  # String formatting in SQL
                r'execute\s*\(\s*.*\+.*\)',  # String concatenation in SQL
                r'cursor\.execute\s*\(\s*f["\']',  # f-strings in SQL
            ]
            
            for line_num, line in enumerate(lines, 1):
                for pattern in sqli_patterns:
                    if re.search(pattern, line):
                        findings.append({
                            'type': 'sqli',
                            'severity': 'high',
                            'file': file_path,
                            'line': line_num,
                            'description': 'Potential SQLinjection via string formatting',
                            'evidence': line.strip(),
                            'remediation': 'Use parameterized queries or ORMs',
                            'source': 'static',
                            'confidence': 0.8
                        })
        
        # Command Injection (RCE) patterns
        if 'rce' in modules:
            rce_patterns = [
                r'os\.system\s*\(',
                r'subprocess\.call\s*\(',
                r'eval\s*\(',
                r'exec\s*\(',
            ]
            
            for line_num, line in enumerate(lines, 1):
                for pattern in rce_patterns:
                    if re.search(pattern, line):
                        # Check if user input is involved
                        if any(keyword in line for keyword in ['request', 'input', 'argv', 'get', 'post']):
                            findings.append({
                                'type': 'rce',
                                'severity': 'critical',
                                'file': file_path,
                                'line': line_num,
                                'description': 'Command injection risk with user input',
                                'evidence': line.strip(),
                                'remediation': 'Avoid using dangerous functions with user input',
                                'source': 'static',
                                'confidence': 0.9
                            })
        
        # Path Traversal patterns
        if 'path_traversal' in modules:
            path_patterns = [
                r'open\s*\(\s*.*request',
                r'Path\s*\(\s*.*request',
                r'file\s*=\s*.*request',
            ]
            
            for line_num, line in enumerate(lines, 1):
                for pattern in path_patterns:
                    if re.search(pattern, line, re.IGNORECASE):
                        findings.append({
                            'type': 'path_traversal',
                            'severity': 'high',
                            'file': file_path,
                            'line': line_num,
                            'description': 'Path traversal vulnerability - user input in file operations',
                            'evidence': line.strip(),
                            'remediation': 'Validate and sanitize file paths',
                            'source': 'static',
                            'confidence': 0.7
                        })
        
        # Insecure cryptography
        if 'crypto' in modules:
            crypto_patterns = [
                r'hashlib\.md5\s*\(',
                r'hashlib\.sha1\s*\(',
                r'DES\.',
                r'mode\s*=\s*ECB',
            ]
            
            for line_num, line in enumerate(lines, 1):
                for pattern in crypto_patterns:
                    if re.search(pattern, line):
                        findings.append({
                            'type': 'weak_crypto',
                            'severity': 'medium',
                            'file': file_path,
                            'line': line_num,
                            'description': 'Use of weak cryptographic algorithm',
                            'evidence': line.strip(),
                            'remediation': 'Use modern cryptographic algorithms (SHA-256, AES-GCM)',
                            'source': 'static',
                            'confidence': 1.0
                        })
        
        return findings
    
    def _scan_javascript_patterns(self, content: str, file_path: str, modules: List[str]) -> List[Dict[str, Any]]:
        """Scan JavaScript/TypeScript code for vulnerability patterns"""
        findings = []
        lines = content.split('\n')
        
        # XSS patterns
        if 'xss' in modules:
            xss_patterns = [
                r'innerHTML\s*=',
                r'dangerouslySetInnerHTML',
                r'document\.write\s*\(',
                r'\.html\s*\(',  # jQuery .html()
            ]
            
            for line_num, line in enumerate(lines, 1):
                for pattern in xss_patterns:
                    if re.search(pattern, line):
                        # Check if user input is involved
                        if any(keyword in line for keyword in ['req.', 'params', 'query', 'body', 'input']):
                            findings.append({
                                'type': 'xss',
                                'severity': 'high',
                                'file': file_path,
                                'line': line_num,
                                'description': 'XSS vulnerability - unescaped user input in DOM',
                                'evidence': line.strip(),
                                'remediation': 'Escape user input or use safe APIs',
                                'source': 'static',
                                'confidence': 0.8
                            })
        
        # SQL Injection patterns
        if 'sqli' in modules:
            sqli_patterns = [
                r'query\s*\(\s*["`\'].*\$\{',  # Template literals in SQL
                r'query\s*\(\s*.*\+.*\)',  # String concatenation in SQL
            ]
            
            for line_num, line in enumerate(lines, 1):
                for pattern in sqli_patterns:
                    if re.search(pattern, line):
                        findings.append({
                            'type': 'sqli',
                            'severity': 'high',
                            'file': file_path,
                            'line': line_num,
                            'description': 'SQL injection via string interpolation',
                            'evidence': line.strip(),
                            'remediation': 'Use parameterized queries',
                            'source': 'static',
                            'confidence': 0.8
                        })
        
        # Command Injection
        if 'rce' in modules:
            rce_patterns = [
                r'exec\s*\(',
                r'spawn\s*\(',
                r'execSync\s*\(',
            ]
            
            for line_num, line in enumerate(lines, 1):
                for pattern in rce_patterns:
                    if re.search(pattern, line):
                        if any(keyword in line for keyword in ['req.', 'params', 'query', 'body']):
                            findings.append({
                                'type': 'rce',
                                'severity': 'critical',
                                'file': file_path,
                                'line': line_num,
                                'description': 'Command injection with user input',
                                'evidence': line.strip(),
                                'remediation': 'Avoid executing user-controlled commands',
                                'source': 'static',
                                'confidence': 0.9
                            })
        
        return findings

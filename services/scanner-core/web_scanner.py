"""
Web Scanner - Scan websites for vulnerabilities

Handles HTTP requests, crawling, and web-specific vulnerability detection
"""

import asyncio
import aiohttp
from typing import Dict, List, Any, Optional, Set
from urllib.parse import urljoin, urlparse, parse_qs
from bs4 import BeautifulSoup
import re


class WebScanner:
    """Scanner for web applications (URLs)"""
    
    def __init__(self, llm_analyzer, max_depth=2, max_pages=50):
        """
        Initialize web scanner
        
        Args:
            llm_analyzer: LLM analyzer instance
            max_depth: Maximum crawl depth
            max_pages: Maximum pages to scan
        """
        self.llm = llm_analyzer
        self.max_depth = max_depth
        self.max_pages = max_pages
        self.visited_urls = set()
        self.session = None
    
    async def scan_url(self, start_url: str, modules: List[str] = None) -> List[Dict[str, Any]]:
        """
        Scan website starting from URL
        
        Args:
            start_url: Starting URL
            modules: Vulnerability modules to check
            
        Returns:
            List of vulnerability findings
        """
        if modules is None or 'all' in modules:
            modules = ['xss', 'sqli', 'headers', 'info_disclosure', 'ssl']
        
        all_findings = []
        
        # Create persistent session
        async with aiohttp.ClientSession() as session:
            self.session = session
            
            # Crawl website
            print(f"[Web] Crawling {start_url}...")
            pages = await self._crawl(start_url)
            print(f"[Web] Found {len(pages)} pages to scan")
            
            # Scan each page
            for i, page_data in enumerate(pages):
                print(f"[Web] Scanning page {i+1}/{len(pages)}: {page_data['url']}")
                
                page_findings = await self._scan_page(page_data, modules)
                all_findings.extend(page_findings)
            
            self.session = None
        
        # Deduplicate findings
        unique_findings = self._deduplicate_findings(all_findings)
        
        print(f"[Web] Scan complete: {len(unique_findings)} vulnerabilities found")
        return unique_findings
    
    async def _crawl(self, start_url: str) -> List[Dict[str, Any]]:
        """Crawl website to discover pages"""
        to_visit = [(start_url, 0)]  # (url, depth)
        pages = []
        
        while to_visit and len(pages) < self.max_pages:
            url, depth = to_visit.pop(0)
            
            # Skip if already visited
            if url in self.visited_urls:
                continue
            
            # Skip if too deep
            if depth > self.max_depth:
                continue
            
            self.visited_urls.add(url)
            
            try:
                # Fetch page
                async with self.session.get(url, timeout=10, allow_redirects=True) as response:
                    html = await response.text()
                    headers = dict(response.headers)
                    
                    page_data = {
                        'url': url,
                        'status': response.status,
                        'headers': headers,
                        'html': html,
                        'depth': depth
                    }
                    
                    pages.append(page_data)
                    
                    # Extract links for further crawling
                    if depth < self.max_depth:
                        soup = BeautifulSoup(html, 'html.parser')
                        links = self._extract_links(soup, url, start_url)
                        
                        for link in links:
                            if link not in self.visited_urls:
                                to_visit.append((link, depth + 1))
                
            except Exception as e:
                print(f"[Web] Error crawling {url}: {e}")
        
        return pages
    
    def _extract_links(self, soup: BeautifulSoup, current_url: str, base_url: str) -> List[str]:
        """Extract valid links from page"""
        links = []
        base_domain = urlparse(base_url).netloc
        
        for tag in soup.find_all('a', href=True):
            href = tag['href']
            
            # Resolve relative URLs
            absolute_url = urljoin(current_url, href)
            
            # Only follow links on same domain
            if urlparse(absolute_url).netloc == base_domain:
                # Remove fragment
                url_without_fragment = absolute_url.split('#')[0]
                links.append(url_without_fragment)
        
        return links
    
    async def _scan_page(self, page_data: Dict, modules: List[str]) -> List[Dict[str, Any]]:
        """Scan individual page for vulnerabilities"""
        findings = []
        url = page_data['url']
        
        # 1. Check security headers
        if 'headers' in modules:
            header_findings = self._check_security_headers(page_data)
            findings.extend(header_findings)
        
        # 2. Check for information disclosure
        if 'info_disclosure' in modules:
            info_findings = self._check_information_disclosure(page_data)
            findings.extend(info_findings)
        
        # 3. LLM analysis of page
        if any(m in modules for m in ['xss', 'sqli', 'all']):
            llm_findings = await self.llm.analyze_web_response(
                url,
                'GET',
                {
                    'status': page_data['status'],
                    'headers': page_data['headers'],
                    'body': page_data['html'][:2000]  # First 2000 chars
                }
            )
            findings.extend(llm_findings)
        
        # 4. Check forms for XSS/SQLi
        if 'xss' in modules or 'sqli' in modules:
            soup = BeautifulSoup(page_data['html'], 'html.parser')
            forms = soup.find_all('form')
            
            for form in forms:
                form_findings = await self._analyze_form(url, form, modules)
                findings.extend(form_findings)
        
        return findings
    
    def _check_security_headers(self, page_data: Dict) -> List[Dict[str, Any]]:
        """Check for missing security headers"""
        findings = []
        headers = {k.lower(): v for k, v in page_data['headers'].items()}
        url = page_data['url']
        
        # Check for important security headers
        security_headers = {
            'x-frame-options': 'Missing X-Frame-Options header (Clickjacking risk)',
            'x-content-type-options': 'Missing X-Content-Type-Options header',
            'content-security-policy': 'Missing Content-Security-Policy header',
            'strict-transport-security': 'Missing HSTS header (HTTP allowed)',
            'x-xss-protection': 'Missing X-XSS-Protection header'
        }
        
        for header, description in security_headers.items():
            if header not in headers:
                findings.append({
                    'type': 'missing_security_header',
                    'severity': 'medium' if header != 'content-security-policy' else 'low',
                    'url': url,
                    'description': description,
                    'remediation': f'Add {header} header to HTTP responses',
                    'evidence': f'Header {header} not found in response',
                    'source': 'static',
                    'confidence': 1.0
                })
        
        return findings
    
    def _check_information_disclosure(self, page_data: Dict) -> List[Dict[str, Any]]:
        """Check for information disclosure"""
        findings = []
        headers = page_data['headers']
        html = page_data['html']
        url = page_data['url']
        
        # Check for version disclosure in headers
        disclosure_headers = ['server', 'x-powered-by', 'x-aspnet-version']
        headers_lower = {k.lower(): (k, v) for k, v in headers.items()}
        
        for header in disclosure_headers:
            if header in headers_lower:
                original_key, value = headers_lower[header]
                findings.append({
                    'type': 'info_disclosure',
                    'severity': 'low',
                    'url': url,
                    'description': f'Server version disclosed in {header} header',
                    'evidence': f"{original_key}: {value}",
                    'remediation': f'Remove or obfuscate {header} header',
                    'source': 'static',
                    'confidence': 1.0
                })
        
        # Check for comments with sensitive info
        comments = re.findall(r'<!--(.*?)-->', html, re.DOTALL)
        for comment in comments:
            # Look for potential sensitive patterns
            if any(keyword in comment.lower() for keyword in ['password', 'api key', 'secret', 'token', 'TODO', 'FIXME']):
                findings.append({
                    'type': 'info_disclosure',
                    'severity': 'low',
                    'url': url,
                    'description': 'Sensitive information in HTML comments',
                    'evidence': comment[:100],
                    'remediation': 'Remove sensitive comments from production',
                    'source': 'static',
                    'confidence': 0.7
                })
        
        return findings
    
    async def _analyze_form(self, url: str, form, modules: List[str]) -> List[Dict[str, Any]]:
        """Analyze form for vulnerabilities"""
        findings = []
        
        # Get form action and method
        action = form.get('action', '')
        method = form.get('method', 'get').upper()
        
        # Get all input fields
        inputs = form.find_all('input')
        
        # Check for CSRF token
        has_csrf_token = any(
            'csrf' in input_tag.get('name', '').lower() or
            'csrf' in input_tag.get('id', '').lower()
            for input_tag in inputs
        )
        
        if method == 'POST' and not has_csrf_token:
            findings.append({
                'type': 'csrf',
                'severity': 'medium',
                'url': url,
                'description': 'Form lacks CSRF protection',
                'evidence': f'POST form at {url} has no CSRF token',
                'remediation': 'Implement CSRF tokens for state-changing operations',
                'source': 'static',
                'confidence': 0.9
            })
        
        return findings
    
    def _deduplicate_findings(self, findings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate findings"""
        seen = set()
        unique = []
        
        for finding in findings:
            # Create unique key
            key = (
                finding.get('type'),
                finding.get('url'),
                finding.get('description')[:50]  # First 50 chars
            )
            
            if key not in seen:
                seen.add(key)
                unique.append(finding)
        
        return unique

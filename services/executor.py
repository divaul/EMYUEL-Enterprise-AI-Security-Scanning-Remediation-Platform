"""
Executor - Dynamic Tool Orchestration Engine

Executes testing steps based on AI-generated instructions.
Maps AI commands to actual security scanning tools.
"""

import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

# Import detectors - note: directory is 'scanner-core' with hyphen
try:
    # Try importing from scanner-core directory
    sys.path.insert(0, str(Path(__file__).parent / 'scanner-core'))
    from detectors.xss_detector import XSSDetector
    from detectors.injection_detector import SQLInjectionDetector  
    from detectors.brute_force_detector import BruteForceDetector
except ImportError as e:
    # Fallback: detectors not available
    print(f"[WARNING] Could not import detectors: {e}")
    XSSDetector = None
    SQLInjectionDetector = None
    BruteForceDetector = None

# Import AI Planner classes
from ai_planner import TestStep, RiskLevel


@dataclass
class ExecutionResult:
    """Result from executing a test step"""
    step_number: int
    step_name: str
    success: bool
    findings: List[Dict[str, Any]]
    execution_time: float
    error: Optional[str] = None
    raw_output: Optional[Dict] = None
    
    def to_dict(self):
        return {
            'step_number': self.step_number,
            'step_name': self.step_name,
            'success': self.success,
            'findings': self.findings,
            'execution_time': self.execution_time,
            'error': self.error,
            'raw_output': self.raw_output
        }


class Executor:
    """
    Dynamic tool executor based on AI instructions
    
    Translates AI-generated test steps into actual
    tool executions and collects results.
    """
    
    # Tool mapping: AI tool name -> actual implementation
    TOOL_REGISTRY = {
        'XSSDetector': XSSDetector,
        'SQLInjectionDetector': SQLInjectionDetector,
        'BruteForceDetector': BruteForceDetector,
        'HeaderAnalyzer': 'header_analyzer',  # Built-in
        'TechDetector': 'tech_detector',      # Built-in
    }
    
    # Method mapping: AI method name -> executor method
    METHOD_MAPPING = {
        'xss_scan': '_execute_xss_scan',
        'sql_injection_scan': '_execute_sql_injection_scan',
        'brute_force_common_credentials': '_execute_brute_force',
        'brute_force_exhaustive': '_execute_brute_force_exhaustive',
        'analyze_headers': '_execute_header_analysis',
        'fingerprint_technology': '_execute_tech_fingerprint',
        'enumerate_endpoints': '_execute_endpoint_enum',
        'test_csrf': '_execute_csrf_test',
    }
    
    def __init__(self, verbose: bool = True):
        """
        Initialize executor
        
        Args:
            verbose: Enable detailed logging
        """
        self.verbose = verbose
        self.executions_count = 0
        self.total_findings = 0
    
    def log(self, message: str):
        """Conditional logging"""
        if self.verbose:
            print(f"[EXECUTOR] {message}")
    
    async def execute_step(self, step: TestStep, target_url: str) -> ExecutionResult:
        """
        Execute a single test step
        
        Args:
            step: TestStep from AI planner
            target_url: Target URL to test
            
        Returns:
            ExecutionResult with findings
        """
        self.log(f"Executing step {step.step_number}: {step.name}")
        self.log(f"Method: {step.method}, Tool: {step.tool}")
        
        start_time = datetime.now()
        
        try:
            # Map method to executor function
            if step.method in self.METHOD_MAPPING:
                method_name = self.METHOD_MAPPING[step.method]
                executor_method = getattr(self, method_name)
                
                # Execute
                findings, raw_output = await executor_method(
                    target_url=target_url,
                    params=step.params
                )
                
                execution_time = (datetime.now() - start_time).total_seconds()
                
                self.executions_count += 1
                self.total_findings += len(findings)
                
                self.log(f"Step completed: {len(findings)} findings in {execution_time:.2f}s")
                
                return ExecutionResult(
                    step_number=step.step_number,
                    step_name=step.name,
                    success=True,
                    findings=findings,
                    execution_time=execution_time,
                    raw_output=raw_output
                )
            
            else:
                # Unknown method
                self.log(f"Unknown method: {step.method}")
                return ExecutionResult(
                    step_number=step.step_number,
                    step_name=step.name,
                    success=False,
                    findings=[],
                    execution_time=0,
                    error=f"Unknown method: {step.method}"
                )
        
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            self.log(f"Step failed: {str(e)}")
            
            return ExecutionResult(
                step_number=step.step_number,
                step_name=step.name,
                success=False,
                findings=[],
                execution_time=execution_time,
                error=str(e)
            )
    
    async def _execute_xss_scan(self, target_url: str, params: Dict) -> tuple:
        """Execute XSS vulnerability scan"""
        self.log("Running XSS scan...")
        
        # Simplified XSS detection (pattern-based)
        # Real XSSDetector requires LLM, so we use basic testing here
        import aiohttp
        
        test_payloads = [
            '<script>alert(1)</script>',
            '"><script>alert(1)</script>',
            "';alert(1);//"
        ]
        
        findings = []
        try:
            async with aiohttp.ClientSession() as session:
                for payload in test_payloads:
                    # Test in query parameters
                    test_url = f"{target_url}?test={payload}"
                    async with session.get(test_url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                        content = await response.text()
                        
                        # Check if payload reflected without encoding
                        if payload in content:
                            findings.append({
                                'type': 'XSS',
                                'severity': 'HIGH',
                                'location': target_url,
                                'payload': payload,
                                'description': f'Cross-Site Scripting: payload reflected without encoding'
                            })
                            break  # Found one, that's enough
        except Exception as e:
            self.log(f"XSS scan error: {e}")
        
        results = {
            'vulnerable': len(findings) > 0,
            'vulnerabilities': findings,
            'tested_payloads': len(test_payloads)
        }
        
        return findings, results
    
    async def _execute_sql_injection_scan(self, target_url: str, params: Dict) -> tuple:
        """Execute SQL Injection scan"""
        self.log("Running SQL Injection scan...")
        
        # Simplified SQLi detection (error-based)
        # Real SQLInjectionDetector requires LLM, so we use simple testing
        import aiohttp
        
        test_payloads = [
            "' OR '1'='1",
            "1' OR '1'='1' --",
            "admin'--",
            "' UNION SELECT NULL--"
        ]
        
        sql_errors = [
            'sql syntax',
            'mysql',
            'postgresql',
            'sqlite',
            'ora-',
            'syntax error',
            'unclosed quotation',
            'quoted string not properly terminated'
        ]
        
        findings = []
        try:
            async with aiohttp.ClientSession() as session:
                for payload in test_payloads:
                    test_url = f"{target_url}?id={payload}"
                    async with session.get(test_url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                        content = await response.text()
                        content_lower = content.lower()
                        
                        # Check for SQL errors in response
                        for error in sql_errors:
                            if error in content_lower:
                                findings.append({
                                    'type': 'SQL_INJECTION',
                                    'severity': 'CRITICAL',
                                    'location': target_url,
                                    'payload': payload,
                                    'description': f'SQL Injection: database error detected with payload'
                                })
                                break  # Found one
                        if findings:
                            break
        except Exception as e:
            self.log(f"SQL injection scan error: {e}")
        
        results = {
            'vulnerable': len(findings) > 0,
            'vulnerabilities': findings,
            'tested_payloads': len(test_payloads)
        }
        
        return findings, results
    
    async def _execute_brute_force(self, target_url: str, params: Dict) -> tuple:
        """Execute brute force with common credentials"""
        self.log("Running brute force (default credentials)...")
        
        detector = BruteForceDetector(
            strategy='default',
            rate_limit=params.get('rate_limit', 0.5)
        )
        
        results = await detector.detect(target_url)
        
        findings = []
        if results.get('found_credentials'):
            for cred in results['found_credentials']:
                findings.append({
                    'type': 'WEAK_CREDENTIALS',
                    'severity': 'CRITICAL',
                    'location': target_url,
                    'credentials': cred,
                    'description': f'Weak credentials found: {cred[0]}:{cred[1]}'
                })
        
        return findings, results
    
    async def _execute_brute_force_exhaustive(self, target_url: str, params: Dict) -> tuple:
        """Execute exhaustive brute force"""
        self.log("Running exhaustive brute force...")
        self.log(f"WARNING: This may take a long time!")
        
        detector = BruteForceDetector(
            strategy='exhaustive',
            charsets=params.get('charsets', ['lowercase', 'numbers']),
            min_length=params.get('min_length', 1),
            max_length=params.get('max_length', 4),
            rate_limit=params.get('rate_limit', 0.1),
            max_attempts=params.get('max_attempts', 10000)
        )
        
        results = await detector.detect(target_url)
        
        findings = []
        if results.get('found_credentials'):
            for cred in results['found_credentials']:
                findings.append({
                    'type': 'WEAK_CREDENTIALS',
                    'severity': 'CRITICAL',
                    'location': target_url,
                    'credentials': cred,
                    'description': f'Password cracked: {cred[1]}'
                })
        
        return findings, results
    
    async def _execute_header_analysis(self, target_url: str, params: Dict) -> tuple:
        """Analyze security headers"""
        self.log("Analyzing security headers...")
        
        import aiohttp
        
        async with aiohttp.ClientSession() as session:
            async with session.get(target_url) as response:
                headers = dict(response.headers)
        
        findings = []
        security_headers = {
            'X-Frame-Options': 'Clickjacking protection',
            'X-Content-Type-Options': 'MIME-sniffing protection',
            'Content-Security-Policy': 'XSS and injection protection',
            'Strict-Transport-Security': 'HTTPS enforcement',
            'X-XSS-Protection': 'XSS filter'
        }
        
        for header, purpose in security_headers.items():
            if header not in headers:
                findings.append({
                    'type': 'MISSING_SECURITY_HEADER',
                    'severity': 'MEDIUM',
                    'location': target_url,
                    'header': header,
                    'description': f'Missing {header} - {purpose}'
                })
        
        return findings, {'headers': headers, 'missing': [f['header'] for f in findings]}
    
    async def _execute_tech_fingerprint(self, target_url: str, params: Dict) -> tuple:
        """Technology fingerprinting"""
        self.log("Fingerprinting technologies...")
        
        import aiohttp
        
        async with aiohttp.ClientSession() as session:
            async with session.get(target_url) as response:
                headers = dict(response.headers)
                content = await response.text()
        
        technologies = []
        
        # Server
        if 'Server' in headers:
            technologies.append({'name': headers['Server'], 'category': 'Web Server'})
        
        # Framework detection
        if 'X-Powered-By' in headers:
            technologies.append({'name': headers['X-Powered-By'], 'category': 'Framework'})
        
        # Content-based
        content_lower = content.lower()
        if 'wordpress' in content_lower:
            technologies.append({'name': 'WordPress', 'category': 'CMS'})
        if 'react' in content_lower:
            technologies.append({'name': 'React', 'category': 'JavaScript Framework'})
        
        findings = []  # Tech fingerprinting doesn't produce vulnerability findings
        
        return findings, {'technologies': technologies}
    
    async def _execute_endpoint_enum(self, target_url: str, params: Dict) -> tuple:
        """Enumerate endpoints (simple crawler)"""
        self.log("Enumerating endpoints...")
        
        # Simple implementation - just common paths
        common_paths = [
            '/admin', '/login', '/api', '/config',
            '/backup', '/test', '/debug', '/upload'
        ]
        
        import aiohttp
        
        found_endpoints = []
        
        async with aiohttp.ClientSession() as session:
            for path in common_paths:
                try:
                    url = target_url.rstrip('/') + path
                    async with session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as response:
                        if response.status < 400:
                            found_endpoints.append({
                                'url': url,
                                'status': response.status
                            })
                            self.log(f"Found: {url} [{response.status}]")
                except:
                    pass
        
        findings = []
        for endpoint in found_endpoints:
            if endpoint['status'] == 200:
                findings.append({
                    'type': 'EXPOSED_ENDPOINT',
                    'severity': 'LOW',
                    'location': endpoint['url'],
                    'description': f'Accessible endpoint: {endpoint["url"]}'
                })
        
        return findings, {'endpoints': found_endpoints}
    
    async def _execute_csrf_test(self, target_url: str, params: Dict) -> tuple:
        """Test CSRF protection"""
        self.log("Testing CSRF protection...")
        
        import aiohttp
        from bs4 import BeautifulSoup
        
        async with aiohttp.ClientSession() as session:
            async with session.get(target_url) as response:
                content = await response.text()
        
        soup = BeautifulSoup(content, 'html.parser')
        forms = soup.find_all('form')
        
        findings = []
        
        for i, form in enumerate(forms):
            # Check for CSRF token
            has_csrf = False
            for input_tag in form.find_all('input'):
                input_name = input_tag.get('name', '').lower()
                if any(token in input_name for token in ['csrf', 'token', '_token', 'authenticity']):
                    has_csrf = True
                    break
            
            if not has_csrf:
                findings.append({
                    'type': 'MISSING_CSRF_PROTECTION',
                    'severity': 'HIGH',
                    'location': target_url,
                    'form_index': i,
                    'description': f'Form #{i} missing CSRF protection'
                })
        
        return findings, {'forms_checked': len(forms), 'vulnerable_forms': len(findings)}


# Example usage
if __name__ == '__main__':
    async def test_executor():
        from services.ai_planner import TestStep, RiskLevel
        
        executor = Executor(verbose=True)
        
        # Test step
        step = TestStep(
            step_number=1,
            name="Security Headers Check",
            objective="Find missing security headers",
            method="analyze_headers",
            tool="HeaderAnalyzer",
            params={},
            risk_level=RiskLevel.LOW,
            estimated_time=30,
            requires_approval=False
        )
        
        result = await executor.execute_step(step, "https://example.com")
        print(f"\nResult: {result.to_dict()}")
    
    # asyncio.run(test_executor())
    print("Executor module loaded")

"""
Natural Language Parser for EMYUEL

Converts natural language queries into structured scan parameters.
Supports English and Indonesian language.
"""

import re
from typing import Dict, List, Any, Optional
from enum import Enum


class ScanIntent(Enum):
    """Intent types for user queries"""
    SCAN = "scan"
    CONFIGURE = "configure"
    REPORT = "report"
    HELP = "help"
    UNKNOWN = "unknown"


class NLPParser:
    """
    Natural Language Parser for security scan queries
    
    Examples:
        "find XSS in login page" → {target: "login", modules: ["xss"]}
        "scan website editor for SQL injection" → {target: "website/editor", modules: ["sqli"]}
        "cari celah keamanan di admin panel" → {target: "admin", modules: ["all"]}
    """
    
    def __init__(self):
        # Vulnerability type mappings
        self.vulnerability_keywords = {
            # English
            'xss': ['xss', 'cross-site scripting', 'cross site scripting'],
            'sqli': ['sql injection', 'sqli', 'sql', 'database injection', 'database attack', 'database security', 'database vulnerability'],
            'ssrf': ['ssrf', 'server-side request forgery', 'server side request'],
            'rce': ['rce', 'remote code execution', 'command injection'],
            'csrf': ['csrf', 'cross-site request forgery', 'cross site request'],
            'path_traversal': ['path traversal', 'directory traversal', 'lfi', 'local file inclusion'],
            'auth': ['authentication', 'auth bypass', 'authorization', 'access control', 'brute force', 'login'],
            'deserialization': ['deserialization', 'unsafe deserialization'],
            'headers': ['security headers', 'header security', 'http headers'],
            
            # Indonesian
            'xss_id': ['skrip lintas situs', 'injeksi skrip', 'celah xss'],
            'sqli_id': ['injeksi sql', 'serangan database', 'keamanan database', 'celah database', 'database', 'databasenya'],
            'all_id': ['semua', 'seluruh', 'keseluruhan', 'semua kerentanan', 'semua celah'],
            'auth_id': ['autentikasi', 'login', 'akses', 'brute force'],
            'headers_id': ['header keamanan', 'header http', 'header'],
        }
        
        # Action keywords
        self.scan_keywords = [
            'scan', 'find', 'search', 'check', 'analyze', 'test', 'audit',
            'cari', 'temukan', 'periksa', 'analisis', 'tes', 'uji'
        ]
        
        # Target keywords
        self.target_indicators = [
            'in', 'on', 'at', 'for', 'di', 'pada', 'bagian'
        ]
        
        # Security keywords
        self.security_keywords = [
            'vulnerability', 'vulnerabilities', 'security', 'issue', 'issues',
            'flaw', 'flaws', 'weakness', 'weaknesses', 'bug', 'bugs',
            'celah', 'kerentanan', 'keamanan', 'masalah', 'kelemahan'
        ]
    
    def parse(self, query: str) -> Dict[str, Any]:
        """
        Parse natural language query into structured parameters
        
        Args:
            query: Natural language query string
            
        Returns:
            Dictionary with parsed parameters:
            {
                'intent': ScanIntent,
                'target': str,
                'modules': List[str],
                'scope': str,  # 'full' or 'targeted'
                'confidence': float  # 0.0 to 1.0
            }
        """
        query = query.lower().strip()
        
        result = {
            'intent': self._classify_intent(query),
            'target': self._extract_target(query),
            'modules': self._extract_modules(query),
            'scope': 'full',
            'confidence': 0.0,
            'original_query': query
        }
        
        # Determine scope
        if result['target'] or (result['modules'] and 'all' not in result['modules']):
            result['scope'] = 'targeted'
        
        # Calculate confidence
        result['confidence'] = self._calculate_confidence(query, result)
        
        return result
    
    def _classify_intent(self, query: str) -> ScanIntent:
        """Classify the intent of the query"""
        
        # Check for scan intent
        for keyword in self.scan_keywords:
            if keyword in query:
                return ScanIntent.SCAN
        
        # Check for configuration
        if any(word in query for word in ['config', 'configure', 'setup', 'key', 'api']):
            return ScanIntent.CONFIGURE
        
        # Check for report
        if any(word in query for word in ['report', 'generate', 'export', 'laporan']):
            return ScanIntent.REPORT
        
        # Check for help
        if any(word in query for word in ['help', 'how', 'what', 'bantuan', 'cara']):
            return ScanIntent.HELP
        
        # Default to scan if contains security keywords
        if any(word in query for word in self.security_keywords):
            return ScanIntent.SCAN
        
        return ScanIntent.UNKNOWN
    
    def _extract_target(self, query: str) -> Optional[str]:
        """Extract target from query"""
        
        # Common patterns
        patterns = [
            r'(?:in|on|at|di|pada)\s+(?:the\s+)?([a-z_\-/]+(?:\s+[a-z_\-/]+)*)',
            r'(?:bagian|halaman)\s+([a-z_\-/]+)',
            r'([a-z_\-/]+)\s+(?:page|form|panel|editor|component)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, query)
            if match:
                target = match.group(1).strip()
                # Clean up target
                target = re.sub(r'\s+', '/', target)
                return target
        
        # Try to find common targets
        common_targets = [
            'login', 'admin', 'dashboard', 'api', 'upload', 'editor',
            'user', 'profile', 'settings', 'payment', 'checkout',
            'search', 'form', 'register', 'signup'
        ]
        
        for target in common_targets:
            if target in query:
                return target
        
        return None
    
    def _extract_modules(self, query: str) -> List[str]:
        """Extract vulnerability modules to scan"""
        
        modules = []
        
        # Check each vulnerability type
        for module, keywords in self.vulnerability_keywords.items():
            for keyword in keywords:
                if keyword in query:
                    # Map Indonesian to English module names
                    if module.endswith('_id'):
                        module = module.replace('_id', '')
                    
                    if module == 'all':
                        return ['all']
                    
                    if module not in modules:
                        modules.append(module)
        
        # If security keywords found but no specific modules, scan all
        if not modules:
            has_security_keyword = any(word in query for word in self.security_keywords)
            if has_security_keyword:
                modules = ['all']
        
        return modules if modules else ['all']
    
    def _calculate_confidence(self, query: str, result: Dict[str, Any]) -> float:
        """Calculate confidence score for the parsing"""
        
        confidence = 0.0
        
        # Intent confidence
        if result['intent'] != ScanIntent.UNKNOWN:
            confidence += 0.3
        
        # Target confidence
        if result['target']:
            confidence += 0.3
        
        # Modules confidence
        if result['modules']:
            confidence += 0.2
        
        # Action keyword presence
        if any(keyword in query for keyword in self.scan_keywords):
            confidence += 0.1
        
        # Security keyword presence
        if any(keyword in query for keyword in self.security_keywords):
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def format_structured_command(self, parsed: Dict[str, Any]) -> str:
        """
        Convert parsed result to structured CLI command
        
        Args:
            parsed: Parsed query result
            
        Returns:
            Structured CLI command string
        """
        
        if parsed['intent'] != ScanIntent.SCAN:
            return ""
        
        parts = ["emyuel scan"]
        
        if parsed['target']:
            parts.append(f"--target {parsed['target']}")
        
        if parsed['modules'] and 'all' not in parsed['modules']:
            modules_str = ','.join(parsed['modules'])
            parts.append(f"--modules {modules_str}")
        
        return ' '.join(parts)


# Helper functions for easy imports
def parse_query(query: str) -> Dict[str, Any]:
    """Quick parse function"""
    parser = NLPParser()
    return parser.parse(query)


def query_to_command(query: str) -> str:
    """Convert natural language to CLI command"""
    parser = NLPParser()
    parsed = parser.parse(query)
    return parser.format_structured_command(parsed)


# Example usage
if __name__ == "__main__":
    parser = NLPParser()
    
    # Test cases
    test_queries = [
        "find XSS in login page",
        "scan website editor for SQL injection",
        "cari celah keamanan di admin panel",
        "check for vulnerabilities in API endpoints",
        "test authentication bypass in user profile",
        "analyze security issues",
    ]
    
    print("=== NLP Parser Test Results ===\n")
    for query in test_queries:
        result = parser.parse(query)
        command = parser.format_structured_command(result)
        
        print(f"Query: {query}")
        print(f"Intent: {result['intent'].value}")
        print(f"Target: {result['target']}")
        print(f"Modules: {result['modules']}")
        print(f"Scope: {result['scope']}")
        print(f"Confidence: {result['confidence']:.2f}")
        print(f"Command: {command}")
        print("-" * 50)

"""
Scanner Core - Main vulnerability scanning engine

Orchestrates web and code scanning with LLM analysis
"""

import asyncio
from typing import Dict, Any, Optional, List
from pathlib import Path
from datetime import datetime

# Import scanner components - use try/except for flexibility
try:
    # Try relative import first (when imported as package)
    from .llm_analyzer import LLMAnalyzer
    from .web_scanner import WebScanner
    from .code_scanner import CodeScanner
    from .api_key_manager import APIKeyManager
except ImportError:
    # Fall back to direct import (when run directly)
    from llm_analyzer import LLMAnalyzer
    from web_scanner import WebScanner
    from code_scanner import CodeScanner
    from api_key_manager import APIKeyManager


class ScannerCore:
    """Main scanner engine - REAL IMPLEMENTATION"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize scanner core
        
        Args:
            config: Scanner configuration
        """
        self.config = config or {}
        
        # Get API key manager
        api_key_manager = self.config.get('api_key_manager')
        if api_key_manager is None:
            api_key_manager = APIKeyManager()
        
        # Get LLM provider
        provider = self.config.get('provider', 'openai')
        
        # Initialize LLM analyzer
        self.llm_analyzer = LLMAnalyzer(api_key_manager, provider)
        
        # Initialize scanners
        self.web_scanner = WebScanner(
            self.llm_analyzer,
            max_depth=self.config.get('max_depth', 2),
            max_pages=self.config.get('max_pages', 50)
        )
        
        self.code_scanner = CodeScanner(self.llm_analyzer)
        
        print(f"[Scanner] Initialized with provider: {provider}")
    
    async def scan(self, target: str, **kwargs) -> Dict[str, Any]:
        """
        Main scan entry point
        
        Args:
            target: URL or directory path to scan
            **kwargs: Additional scan parameters
                - modules: List of vulnerability modules
                - scan_id: Scan identifier
                - profile: Scan profile (quick/standard/comprehensive)
                
        Returns:
            Scan results with findings
        """
        scan_id = kwargs.get('scan_id', f"scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        modules = kwargs.get('modules')
        profile = kwargs.get('profile', 'standard')
        
        print(f"[Scanner] Starting scan: {scan_id}")
        print(f"[Scanner] Target: {target}")
        print(f"[Scanner] Profile: {profile}")
        
        start_time = datetime.now()
        
        # Detect target type
        is_url = target.startswith(('http://', 'https://'))
        
        if is_url:
            print(f"[Scanner] Detected web target")
            findings = await self._scan_web(target, modules)
            target_type = 'web'
        else:
            print(f"[Scanner] Detected code target")
            findings = await self._scan_code(target, modules)
            target_type = 'code'
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Format results
        results = self._format_results(
            scan_id=scan_id,
            target=target,
            target_type=target_type,
            findings=findings,
            start_time=start_time,
            end_time=end_time,
            duration=duration
        )
        
        print(f"[Scanner] Scan complete: {len(findings)} vulnerabilities found in {duration:.1f}s")
        
        return results
    
    async def _scan_web(self, url: str, modules: Optional[List[str]]) -> List[Dict[str, Any]]:
        """Scan website"""
        try:
            findings = await self.web_scanner.scan_url(url, modules)
            return findings
        except Exception as e:
            print(f"[Scanner] Web scan error: {e}")
            return []
    
    async def _scan_code(self, directory: str, modules: Optional[List[str]]) -> List[Dict[str, Any]]:
        """Scan code directory"""
        try:
            findings = await self.code_scanner.scan_directory(directory, modules)
            return findings
        except Exception as e:
            print(f"[Scanner] Code scan error: {e}")
            return []
    
    def _format_results(
        self,
        scan_id: str,
        target: str,
        target_type: str,
        findings: List[Dict[str, Any]],
        start_time: datetime,
        end_time: datetime,
        duration: float
    ) -> Dict[str, Any]:
        """Format scan results"""
        
        # Count by severity
        by_severity = {
            'critical': 0,
            'high': 0,
            'medium': 0,
            'low': 0
        }
        
        for finding in findings:
            severity = finding.get('severity', 'low')
            if severity in by_severity:
                by_severity[severity] += 1
        
        # Count by type
        by_type = {}
        for finding in findings:
            vuln_type = finding.get('type', 'unknown')
            by_type[vuln_type] = by_type.get(vuln_type, 0) + 1
        
        return {
            'scan_id': scan_id,
            'target': target,
            'target_type': target_type,
            'status': 'completed',
            'start_time': start_time.isoformat(),
            'end_time': end_time.isoformat(),
            'duration_seconds': duration,
            'total_findings': len(findings),
            'findings_by_severity': by_severity,
            'findings_by_type': by_type,
            'findings': findings,
            'llm_usage': self.llm_analyzer.get_usage_stats()
        }

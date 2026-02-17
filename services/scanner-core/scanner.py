"""
Scanner Core - Main Scanner Engine

Orchestrates vulnerability detection across multiple detectors
"""

import logging
import asyncio
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime

from services.llm_orchestrator import create_orchestrator
from .detectors.injection_detector import SQLInjectionDetector
from .detectors.xss_detector import XSSDetector
from .detectors.ssrf_detector import SSRFDetector

logger = logging.getLogger(__name__)


class ScannerCore:
    """Main scanner engine coordinating all detectors"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize scanner core
        
        Args:
            config: Scanner configuration
        """
        self.config = config
        
        # Get LLM config
        llm_config = config.get('llm', {})
        api_key_manager = llm_config.get('api_key_manager')
        provider = llm_config.get('provider', 'openai')
        
        # Create LLMAnalyzer (not orchestrator!)
        if api_key_manager:
            # Import LLMAnalyzer
            import sys
            from pathlib import Path
            scanner_core_dir = Path(__file__).parent
            if str(scanner_core_dir) not in sys.path:
                sys.path.insert(0, str(scanner_core_dir))
            from llm_analyzer import LLMAnalyzer
            
            self.llm = LLMAnalyzer(api_key_manager, provider)
            logger.info(f"LLMAnalyzer initialized with provider: {provider}")
        else:
            logger.warning("No API key manager provided - LLM analysis disabled")
            self.llm = None
        
        # Initialize detectors
        detectors_config = {}
        if self.llm:
            detectors_config = {
                'sqli': SQLInjectionDetector(self.llm),
                'xss': XSSDetector(self.llm),
                'ssrf': SSRFDetector(self.llm)
            }
        self.detectors = detectors_config
        
        logger.info(f"Scanner initialized with {len(self.detectors)} detectors")
    
    async def scan(
        self,
        target: str,
        modules: Optional[List[str]] = None,
        scan_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Scan web target for vulnerabilities
        
        Args:
            target: Target URL to scan
            modules: List of vulnerability types to check
            scan_id: Unique scan ID
            
        Returns:
            Scan results with all findings
        """
        start_time = datetime.utcnow()
        logger.info(f"Starting web scan of target: {target}")
        
        # Detect if target is URL (web) or path (project)
        if target.startswith('http://') or target.startswith('https://'):
            # Web scanning
            return await self._scan_web_target(target, modules, scan_id, start_time)
        else:
            # Project scanning
            return await self.scan_project(target, {'scan_id': scan_id})
    
    async def _scan_web_target(
        self,
        url: str,
        modules: Optional[List[str]],
        scan_id: str,
        start_time: datetime
    ) -> Dict[str, Any]:
        """Scan web target for vulnerabilities"""
        from .web_scanner import WebScanner
        
        # Get SSL verification setting from config
        verify_ssl = self.config.get('verify_ssl', True)
        
        # Create web scanner instance
        web_scanner = WebScanner(
            llm_analyzer=self.llm,
            max_depth=2,
            max_pages=50,
            verify_ssl=verify_ssl
        )
        
        # Run web scan
        logger.info(f"Detected web target: {url}")
        findings = await web_scanner.scan_url(url, modules or ['all'])
        
        # Format results
        end_time = datetime.utcnow()
        duration = (end_time - start_time).total_seconds()
        
        results = {
            'scan_id': scan_id or 'unknown',
            'target': url,
            'target_type': 'web',
            'start_time': start_time.isoformat(),
            'end_time': end_time.isoformat(),
            'duration_seconds': duration,
            'total_findings': len(findings),
            'findings_by_severity': self._count_by_severity(findings),
            'findings_by_type': self._count_by_type(findings),
            'findings': findings
        }
        
        logger.info(f"Web scan completed: {len(findings)} vulnerabilities found in {duration:.2f}s")
        
        return results
    
    async def scan_project(
        self,
        project_path: str,
        scan_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Scan entire project for vulnerabilities
        
        Args:
            project_path: Path to project root
            scan_config: Scan configuration overrides
            
        Returns:
            Scan results with all findings
        """
        start_time = datetime.utcnow()
        logger.info(f"Starting scan of project: {project_path}")
        
        scan_config = scan_config or {}
        enabled_detectors = scan_config.get('detectors', list(self.detectors.keys()))
        
        # Discover source files
        files_to_scan = self._discover_files(project_path, scan_config)
        logger.info(f"Found {len(files_to_scan)} files to scan")
        
        # Scan all files
        all_findings = []
        file_count = 0
        
        for file_info in files_to_scan:
            file_findings = await self._scan_file(
                file_info['path'],
                file_info['content'],
                file_info['context'],
                enabled_detectors
            )
            
            all_findings.extend(file_findings)
            file_count += 1
            
            if file_count % 10 == 0:
                logger.info(f"Scanned {file_count}/{len(files_to_scan)} files...")
        
        # Generate results summary
        end_time = datetime.utcnow()
        duration = (end_time - start_time).total_seconds()
        
        results = {
            'scan_id': scan_config.get('scan_id', 'unknown'),
            'project_path': project_path,
            'start_time': start_time.isoformat(),
            'end_time': end_time.isoformat(),
            'duration_seconds': duration,
            'files_scanned': file_count,
            'total_findings': len(all_findings),
            'findings_by_severity': self._count_by_severity(all_findings),
            'findings_by_type': self._count_by_type(all_findings),
            'findings': all_findings,
            'llm_usage': self.llm.get_usage_stats()
        }
        
        logger.info(f"Scan completed: {len(all_findings)} vulnerabilities found in {duration:.2f}s")
        
        return results
    
    async def _scan_file(
        self,
        file_path: str,
        content: str,
        context: Dict[str, Any],
        enabled_detectors: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Scan single file with all enabled detectors
        
        Args:
            file_path: Path to file
            content: File content
            context: File context (language, framework)
            enabled_detectors: List of detector IDs to use
            
        Returns:
            List of findings for this file
        """
        findings = []
        
        # Run detectors in parallel
        tasks = []
        for detector_id in enabled_detectors:
            if detector_id in self.detectors:
                detector = self.detectors[detector_id]
                tasks.append(detector.analyze(content, file_path, context))
        
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for result in results:
                if isinstance(result, Exception):
                    logger.error(f"Detector error in {file_path}: {str(result)}")
                elif isinstance(result, list):
                    findings.extend(result)
        
        return findings
    
    def _discover_files(
        self,
        project_path: str,
        scan_config: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Discover source files to scan
        
        Args:
            project_path: Project root path
            scan_config: Scan configuration
            
        Returns:
            List of file information dicts
        """
        path = Path(project_path)
        files = []
        
        # Supported extensions
        extensions = scan_config.get('extensions', [
            '.py', '.js', '.ts', '.java', '.php', '.rb', '.go', '.cs', '.cpp'
        ])
        
        # Excluded directories
        exclude_dirs = set(scan_config.get('exclude_dirs', [
            'node_modules', '.git', '__pycache__', 'venv', 'env', 'dist', 'build'
        ]))
        
        for file_path in path.rglob('*'):
            # Skip directories
            if file_path.is_dir():
                continue
            
            # Skip excluded directories
            if any(excluded in file_path.parts for excluded in exclude_dirs):
                continue
            
            # Check extension
            if file_path.suffix not in extensions:
                continue
            
            try:
                content = file_path.read_text(encoding='utf-8', errors='ignore')
                
                files.append({
                    'path': str(file_path),
                    'content': content,
                    'context': {
                        'language': self._detect_language(file_path.suffix),
                        'size': len(content),
                        'lines': content.count('\n')
                    }
                })
            except Exception as e:
                logger.warning(f"Could not read {file_path}: {str(e)}")
        
        return files
    
    def _detect_language(self, extension: str) -> str:
        """Detect programming language from file extension"""
        lang_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.java': 'java',
            '.php': 'php',
            '.rb': 'ruby',
            '.go': 'go',
            '.cs': 'csharp',
            '.cpp': 'cpp'
        }
        return lang_map.get(extension, 'unknown')
    
    def _count_by_severity(self, findings: List[Dict[str, Any]]) -> Dict[str, int]:
        """Count findings by severity"""
        counts = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
        
        for finding in findings:
            severity = finding.get('severity', 'medium').lower()
            if severity in counts:
                counts[severity] += 1
        
        return counts
    
    def _count_by_type(self, findings: List[Dict[str, Any]]) -> Dict[str, int]:
        """Count findings by vulnerability type"""
        counts = {}
        
        for finding in findings:
            vuln_type = finding.get('type', 'unknown')
            counts[vuln_type] = counts.get(vuln_type, 0) + 1
        
        return counts
    
    async def close(self):
        """Cleanup resources"""
        await self.llm.close()

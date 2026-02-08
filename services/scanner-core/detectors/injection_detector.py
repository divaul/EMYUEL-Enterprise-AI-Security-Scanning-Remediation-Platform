"""
SQL Injection Detector

Detects SQL injection vulnerabilities using LLM-powered data flow analysis
"""

import logging
from typing import Dict, List, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class SQLInjectionDetector:
    """SQL Injection vulnerability detector"""
    
    # Common SQL injection entry points
    ENTRY_POINTS = [
        "request.GET",
        "request.POST",
        "request.args",
        "request.form",
        "request.json",
        "request.query_params",
        "request.path_params",
        "params",
        "query_string",
        "input()",
        "sys.argv"
    ]
    
    # Dangerous SQL operations (sinks)
    DANGEROUS_SINKS = [
        "execute(",
        "executemany(",
        "raw(",
        "cursor.execute(",
        "db.execute(",
        "query(",
        "filter(",
        "where(",
        "sql =",
        "query =",
        ".raw_sql(",
        "connection.execute("
    ]
    
    def __init__(self, llm_orchestrator):
        """
        Initialize detector
        
        Args:
            llm_orchestrator: LLM orchestrator instance
        """
        self.llm = llm_orchestrator
    
    async def analyze(self, source_code: str, file_path: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Analyze code for SQL injection vulnerabilities
        
        Args:
            source_code: Source code to analyze
            file_path: Path to the source file
            context: Additional context (language, framework, etc.)
            
        Returns:
            List of vulnerability findings
        """
        logger.info(f"Analyzing {file_path} for SQL injection vulnerabilities")
        
        findings = []
        
        # Step 1: Quick pattern matching for potential issues
        has_sql_operations = any(sink in source_code for sink in self.DANGEROUS_SINKS)
        has_user_input = any(entry in source_code for entry in self.ENTRY_POINTS)
        
        if not (has_sql_operations and has_user_input):
            logger.debug(f"No SQL operations or user input found in {file_path}")
            return findings
        
        # Step 2: Use LLM for deep data flow analysis
        try:
            analysis_result = await self.llm.trace_data_flow(
                source_code=source_code,
                entry_points=self.ENTRY_POINTS,
                dangerous_sinks=self.DANGEROUS_SINKS,
                context={
                    "file_path": file_path,
                    "vulnerability_type": "SQL Injection",
                    "language": context.get("language", "unknown"),
                    "framework": context.get("framework", "unknown")
                }
            )
            
            # Step 3: Process analysis results
            for finding in analysis_result.findings:
                if finding.get("exploitable", False):
                    vulnerability = {
                        "type": "SQL Injection",
                        "severity": finding.get("severity", "medium"),
                        "file_path": file_path,
                        "source": finding.get("source", "unknown"),
                        "sink": finding.get("sink", "unknown"),
                        "flow_path": finding.get("flow_steps", []),
                        "sanitization": finding.get("sanitization", "none"),
                        "description": self._generate_description(finding),
                        "attack_vector": finding.get("attack_vector", ""),
                        "confidence": analysis_result.confidence_score,
                        "provider": analysis_result.provider.value,
                        "cwe": "CWE-89"
                    }
                    
                    findings.append(vulnerability)
                    logger.warning(f"SQL Injection found in {file_path}: {vulnerability['source']} -> {vulnerability['sink']}")
        
        except Exception as e:
            logger.error(f"Error analyzing {file_path} for SQL injection: {str(e)}")
        
        return findings
    
    def _generate_description(self, finding: Dict[str, Any]) -> str:
        """Generate vulnerability description"""
        source = finding.get("source", "user input")
        sink = finding.get("sink", "SQL query")
        sanitization = finding.get("sanitization", "none")
        
        if sanitization == "none":
            return (
                f"Unsanitized user input from {source} flows directly into {sink}. "
                f"An attacker can inject malicious SQL commands to manipulate database queries, "
                f"potentially leading to unauthorized data access, modification, or deletion."
            )
        else:
            return (
                f"User input from {source} is insufficiently sanitized ({sanitization}) before "
                f"being used in {sink}. While some sanitization exists, it may be bypassable, "
                f"allowing SQL injection attacks."
            )
    
    async def generate_remediation(self, vulnerability: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Generate remediation suggestion for vulnerability
        
        Args:
            vulnerability: Vulnerability details
            
        Returns:
            Remediation patch with code suggestions
        """
        try:
            remediation = await self.llm.generate_remediation(vulnerability)
            return remediation.to_dict()
        except Exception as e:
            logger.error(f"Error generating remediation: {str(e)}")
            return None
    
    async def calculate_cvss(self, vulnerability: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Calculate CVSS score for vulnerability
        
        Args:
            vulnerability: Vulnerability details
            
        Returns:
            CVSS score details
        """
        try:
            cvss = await self.llm.calculate_cvss(vulnerability)
            return cvss.to_dict()
        except Exception as e:
            logger.error(f"Error calculating CVSS: {str(e)}")
            return None

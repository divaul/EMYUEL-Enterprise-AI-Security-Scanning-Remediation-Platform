"""
XSS (Cross-Site Scripting) Detector

Detects XSS vulnerabilities including reflected, stored, and DOM-based XSS
"""

import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


class XSSDetector:
    """XSS vulnerability detector"""
    
    # User input sources
    ENTRY_POINTS = [
        "request.GET",
        "request.POST",
        "request.args",
        "request.form",
        "request.json",
        "request.cookies",
        "request.headers",
        "query_params",
        "path_params",
        "document.location",
        "window.location",
        "document.URL",
        "document.referrer"
    ]
    
    # Dangerous output contexts (sinks)
    DANGEROUS_SINKS = [
        "innerHTML",
        "outerHTML",
        "document.write(",
        "document.writeln(",
        ".html(",
        "render(",
        "template(",
        "eval(",
        "setTimeout(",
        "setInterval(",
        "dangerouslySetInnerHTML",
        "v-html",
        "[innerHTML]"
    ]
    
    def __init__(self, llm_orchestrator):
        """Initialize XSS detector"""
        self.llm = llm_orchestrator
    
    async def analyze(self, source_code: str, file_path: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Analyze code for XSS vulnerabilities
        
        Args:
            source_code: Source code to analyze
            file_path: Path to the source file
            context: Additional context
            
        Returns:
            List of XSS vulnerability findings
        """
        logger.info(f"Analyzing {file_path} for XSS vulnerabilities")
        
        findings = []
        
        # Quick pre-check
        has_output = any(sink in source_code for sink in self.DANGEROUS_SINKS)
        has_input = any(entry in source_code for entry in self.ENTRY_POINTS)
        
        if not (has_output and has_input):
            return findings
        
        try:
            # Deep analysis with LLM
            analysis_result = await self.llm.trace_data_flow(
                source_code=source_code,
                entry_points=self.ENTRY_POINTS,
                dangerous_sinks=self.DANGEROUS_SINKS,
                context={
                    "file_path": file_path,
                    "vulnerability_type": "Cross-Site Scripting (XSS)",
                    "language": context.get("language", "unknown"),
                    "framework": context.get("framework", "unknown")
                }
            )
            
            for finding in analysis_result.findings:
                if finding.get("exploitable", False):
                    xss_type = self._determine_xss_type(finding)
                    
                    vulnerability = {
                        "type": f"XSS - {xss_type}",
                        "severity": finding.get("severity", "high"),
                        "file_path": file_path,
                        "source": finding.get("source", "unknown"),
                        "sink": finding.get("sink", "unknown"),
                        "flow_path": finding.get("flow_steps", []),
                        "sanitization": finding.get("sanitization", "none"),
                        "xss_type": xss_type,
                        "description": self._generate_description(finding, xss_type),
                        "attack_vector": finding.get("attack_vector", ""),
                        "confidence": analysis_result.confidence_score,
                        "provider": analysis_result.provider.value,
                        "cwe": self._get_cwe_for_type(xss_type)
                    }
                    
                    findings.append(vulnerability)
                    logger.warning(f"{xss_type} XSS found in {file_path}")
        
        except Exception as e:
            logger.error(f"Error analyzing {file_path} for XSS: {str(e)}")
        
        return findings
    
    def _determine_xss_type(self, finding: Dict[str, Any]) -> str:
        """Determine type of XSS (Reflected, Stored, DOM-based)"""
        sink = finding.get("sink", "").lower()
        source = finding.get("source", "").lower()
        
        # DOM-based XSS indicators
        if any(x in sink for x in ["innerhtml", "outerhtml", "document.write"]):
            if any(x in source for x in ["document.location", "window.location", "document.url"]):
                return "DOM-based"
        
        # Check if data is stored (database, file, etc.)
        flow_steps = finding.get("flow_steps", [])
        if any("database" in step.lower() or "save" in step.lower() for step in flow_steps):
            return "Stored"
        
        # Default to Reflected if coming from HTTP request
        return "Reflected"
    
    def _get_cwe_for_type(self, xss_type: str) -> str:
        """Get CWE ID for XSS type"""
        cwe_map = {
            "Reflected": "CWE-79",
            "Stored": "CWE-79",
            "DOM-based": "CWE-79"
        }
        return cwe_map.get(xss_type, "CWE-79")
    
    def _generate_description(self, finding: Dict[str, Any], xss_type: str) -> str:
        """Generate XSS vulnerability description"""
        source = finding.get("source", "user input")
        sink = finding.get("sink", "output")
        
        descriptions = {
            "Reflected": (
                f"User input from {source} is reflected back to the user through {sink} without proper encoding. "
                f"An attacker can inject malicious JavaScript that executes in the victim's browser."
            ),
            "Stored": (
                f"User input from {source} is stored and later rendered through {sink} without sanitization. "
                f"This allows persistent XSS attacks affecting all users who view the content."
            ),
            "DOM-based": (
                f"Client-side JavaScript reads from {source} and writes to {sink} without validation. "
                f"An attacker can manipulate the DOM to execute malicious scripts entirely on the client side."
            )
        }
        
        return descriptions.get(xss_type, f"XSS vulnerability: {source} -> {sink}")
    
    async def generate_remediation(self, vulnerability: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Generate remediation for XSS vulnerability"""
        try:
            remediation = await self.llm.generate_remediation(vulnerability)
            return remediation.to_dict()
        except Exception as e:
            logger.error(f"Error generating remediation: {str(e)}")
            return None
    
    async def calculate_cvss(self, vulnerability: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Calculate CVSS score for XSS"""
        try:
            cvss = await self.llm.calculate_cvss(vulnerability)
            return cvss.to_dict()
        except Exception as e:
            logger.error(f"Error calculating CVSS: {str(e)}")
            return None

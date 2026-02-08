"""
SSRF (Server-Side Request Forgery) Detector

Detects SSRF vulnerabilities where user input controls server-side HTTP requests
"""

import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


class SSRFDetector:
    """SSRF vulnerability detector"""
    
    ENTRY_POINTS = [
        "request.GET",
        "request.POST",
        "request.args",
        "request.form",
        "request.json",
        "query_params",
        "path_params"
    ]
    
    # HTTP request functions (sinks)
    DANGEROUS_SINKS = [
        "requests.get(",
        "requests.post(",
        "urllib.request(",
        "urllib.urlopen(",
        "httpx.get(",
        "httpx.post(",
        "fetch(",
        "axios.get(",
        "axios.post(",
        "$http.get(",
        "http.get(",
        "curl_exec(",
        "file_get_contents(",
        "readURL(",
        "WebClient",
        "HttpClient"
    ]
    
    def __init__(self, llm_orchestrator):
        """Initialize SSRF detector"""
        self.llm = llm_orchestrator
    
    async def analyze(self, source_code: str, file_path: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Analyze code for SSRF vulnerabilities
        
        Args:
            source_code: Source code to analyze
            file_path: Path to the source file
            context: Additional context
            
        Returns:
            List of SSRF vulnerability findings
        """
        logger.info(f"Analyzing {file_path} for SSRF vulnerabilities")
        
        findings = []
        
        # Pre-check
        has_http_request = any(sink in source_code for sink in self.DANGEROUS_SINKS)
        has_user_input = any(entry in source_code for entry in self.ENTRY_POINTS)
        
        if not (has_http_request and has_user_input):
            return findings
        
        try:
            analysis_result = await self.llm.trace_data_flow(
                source_code=source_code,
                entry_points=self.ENTRY_POINTS,
                dangerous_sinks=self.DANGEROUS_SINKS,
                context={
                    "file_path": file_path,
                    "vulnerability_type": "Server-Side Request Forgery (SSRF)",
                    "language": context.get("language", "unknown"),
                    "framework": context.get("framework", "unknown")
                }
            )
            
            for finding in analysis_result.findings:
                if finding.get("exploitable", False):
                    vulnerability = {
                        "type": "SSRF",
                        "severity": self._calculate_severity(finding),
                        "file_path": file_path,
                        "source": finding.get("source", "unknown"),
                        "sink": finding.get("sink", "unknown"),
                        "flow_path": finding.get("flow_steps", []),
                        "sanitization": finding.get("sanitization", "none"),
                        "description": self._generate_description(finding),
                        "attack_vector": finding.get("attack_vector", ""),
                        "impact": self._assess_impact(finding),
                        "confidence": analysis_result.confidence_score,
                        "provider": analysis_result.provider.value,
                        "cwe": "CWE-918"
                    }
                    
                    findings.append(vulnerability)
                    logger.warning(f"SSRF vulnerability found in {file_path}")
        
        except Exception as e:
            logger.error(f"Error analyzing {file_path} for SSRF: {str(e)}")
        
        return findings
    
    def _calculate_severity(self, finding: Dict[str, Any]) -> str:
        """Calculate SSRF severity based on context"""
        # SSRF in cloud environments is typically critical
        flow_steps = " ".join(finding.get("flow_steps", [])).lower()
        
        if any(x in flow_steps for x in ["aws", "gcp", "azure", "metadata", "169.254.169.254"]):
            return "critical"
        
        return finding.get("severity", "high")
    
    def _assess_impact(self, finding: Dict[str, Any]) -> List[str]:
        """Assess potential impact of SSRF"""
        impacts = []
        
        flow = " ".join(finding.get("flow_steps", [])).lower()
        
        if "cloud" in flow or "metadata" in flow:
            impacts.append("Cloud metadata access (credentials, keys)")
        
        if "internal" in flow or "localhost" in flow or "127.0.0.1" in flow:
            impacts.append("Internal network scanning")
            impacts.append("Bypass firewall restrictions")
        
        impacts.extend([
            "Port scanning",
            "Service enumeration",
            "Data exfiltration"
        ])
        
        return impacts
    
    def _generate_description(self, finding: Dict[str, Any]) -> str:
        """Generate SSRF vulnerability description"""
        source = finding.get("source", "user input")
        sink = finding.get("sink", "HTTP request")
        
        return (
            f"User-controlled input from {source} is used to construct server-side HTTP requests "
            f"in {sink} without proper validation. An attacker can force the server to make requests "
            f"to arbitrary URLs, potentially accessing internal services, cloud metadata endpoints, "
            f"or performing port scanning of internal networks."
        )
    
    async def generate_remediation(self, vulnerability: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Generate SSRF remediation"""
        try:
            remediation = await self.llm.generate_remediation(vulnerability)
            return remediation.to_dict()
        except Exception as e:
            logger.error(f"Error generating remediation: {str(e)}")
            return None
    
    async def calculate_cvss(self, vulnerability: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Calculate CVSS score for SSRF"""
        try:
            cvss = await self.llm.calculate_cvss(vulnerability)
            return cvss.to_dict()
        except Exception as e:
            logger.error(f"Error calculating CVSS: {str(e)}")
            return None

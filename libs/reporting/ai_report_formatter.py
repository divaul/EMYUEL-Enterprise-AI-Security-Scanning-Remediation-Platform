"""
AI Report Formatter

Formats security scan results into professional reports following 
international cybersecurity standards (OWASP, NIST, ISO 27001).
"""

import logging
from typing import Dict, List, Any
from datetime import datetime
import json

logger = logging.getLogger(__name__)


class AIReportFormatter:
    """
    Format security reports using AI with international cybersecurity standards
    
    Follows formats from:
    - OWASP Testing Guide
    - NIST Cybersecurity Framework
    - ISO/IEC 27001
    - SANS/CIS Guidelines
    """
    
    def __init__(self, llm_analyzer):
        """
        Initialize AI report formatter
        
        Args:
            llm_analyzer: LLM analyzer instance for AI formatting
        """
        self.llm = llm_analyzer
        logger.info("AI Report Formatter initialized")
    
    async def format_report(self, scan_results: Dict[str, Any], provider: str = None) -> str:
        """
        Format scan results into professional cybersecurity report (async)
        
        Args:
            scan_results: Raw scan results dictionary
            provider: AI provider to use (default: from llm_analyzer)
            
        Returns:
            Markdown-formatted professional report
        """
        logger.info(f"Formatting report with AI (provider: {provider or 'default'})")
        
        # Build comprehensive prompt following international standards
        prompt = self._build_standard_report_prompt(scan_results)
        
        # Get AI formatting
        try:
            # Optionally override provider
            if provider and hasattr(self.llm, 'provider'):
                original_provider = self.llm.provider
                self.llm.provider = provider
            
            ai_response = await self.llm.chat(prompt)  # Now properly awaited
            
            # Restore original provider
            if provider and hasattr(self.llm, 'provider'):
                self.llm.provider = original_provider
            
            logger.info("AI formatting completed successfully")
            return ai_response
            
        except Exception as e:
            logger.error(f"Error during AI formatting: {e}")
            # Fallback to template-based report
            return self._generate_fallback_report(scan_results)
    
    def format_report_sync(self, scan_results: Dict[str, Any], provider: str = None) -> str:
        """
        Synchronous wrapper for format_report() - for use in non-async contexts
        
        Args:
            scan_results: Raw scan results dictionary
            provider: AI provider to use
            
        Returns:
            Markdown-formatted professional report
        """
        import asyncio
        
        try:
            # Try to get existing event loop
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If loop is running, create new loop in thread
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as pool:
                    future = pool.submit(asyncio.run, self.format_report(scan_results, provider))
                    return future.result()
            else:
                # Use existing loop
                return loop.run_until_complete(self.format_report(scan_results, provider))
        except RuntimeError:
            # No event loop, create new one
            return asyncio.run(self.format_report(scan_results, provider))
    
    def _build_standard_report_prompt(self, results: Dict[str, Any]) -> str:
        """
        Build AI prompt following international cybersecurity reporting standards
        
        Format follows:
        - OWASP Testing Guide v4.2
        - NIST SP 800-115 (Technical Guide to Information Security Testing)
        - ISO/IEC 27001:2022
        """
        
        # Extract key metrics
        target = results.get('target', 'Unknown')
        total_findings = results.get('total_findings', 0)
        severity = results.get('findings_by_severity', {})
        findings = results.get('findings', [])
        scan_id = results.get('scan_id', 'N/A')
        start_time = results.get('start_time', 'Unknown')
        duration = results.get('duration_seconds', 0)
        
        # Build per-tool summary
        tool_summary = {}
        for f in findings:
            tool_name = f.get('tool', f.get('source', 'AI Scanner'))
            if tool_name.startswith('external:'):
                tool_name = tool_name.replace('external:', '')
            if tool_name not in tool_summary:
                tool_summary[tool_name] = {'count': 0, 'severities': {}}
            tool_summary[tool_name]['count'] += 1
            sev = f.get('severity', 'info').lower()
            tool_summary[tool_name]['severities'][sev] = tool_summary[tool_name]['severities'].get(sev, 0) + 1
        
        # Format per-tool table
        tool_table_lines = []
        for tool_name, stats in sorted(tool_summary.items(), key=lambda x: x[1]['count'], reverse=True):
            sev_str = ', '.join(f"{k}: {v}" for k, v in sorted(stats['severities'].items()))
            tool_table_lines.append(f"| {tool_name} | {stats['count']} | {sev_str} |")
        tool_table = '\n'.join(tool_table_lines) if tool_table_lines else '| N/A | 0 | N/A |'
        
        # Build findings summary
        findings_json = json.dumps(findings[:20], indent=2)  # Limit to top 20
        
        prompt = f"""You are a certified cybersecurity professional creating a comprehensive vulnerability assessment report following international standards (OWASP, NIST SP 800-115, ISO/IEC 27001).

TARGET INFORMATION:
- Target: {target}
- Scan ID: {scan_id}
- Scan Date: {start_time}
- Duration: {duration:.2f} seconds
- Total Vulnerabilities: {total_findings}

SEVERITY DISTRIBUTION:
- Critical: {severity.get('critical', 0)}
- High: {severity.get('high', 0)}
- Medium: {severity.get('medium', 0)}
- Low: {severity.get('low', 0)}

FINDINGS BY TOOL:
| Tool | Findings | Severity Breakdown |
|------|----------|-------------------|
{tool_table}

VULNERABILITY FINDINGS:
{findings_json}

Create a professional penetration testing report in Markdown format following this EXACT structure:

# VULNERABILITY ASSESSMENT REPORT

## DOCUMENT INFORMATION
- **Report ID:** {scan_id}
- **Assessment Date:** {start_time}
- **Target:** {target}
- **Methodology:** OWASP Testing Guide v4.2, NIST SP 800-115
- **Classification:** CONFIDENTIAL

---

## 1. EXECUTIVE SUMMARY

### 1.1 Overview
Provide a high-level summary of the security assessment in 2-3 paragraphs. Explain what was tested, the methodology used, and the overall security posture.

### 1.2 Risk Rating
Based on findings, provide an overall risk rating:
- **Overall Risk Level:** [Critical/High/Medium/Low]
- **Justification:** Explain why this rating was assigned

### 1.3 Key Findings Summary
List the top 3-5 most critical issues discovered:
1. [Finding 1]
2. [Finding 2]
3. [Finding 3]

### 1.4 Recommendations Summary
High-level recommendations (3-5 bullet points):
- Immediate actions required
- Medium-term improvements
- Long-term security strategy

---

## 2. SCOPE AND METHODOLOGY

### 2.1 Assessment Scope
- **Target Application/System:** {target}
- **Assessment Type:** Automated Security Scan
- **Testing Window:** {start_time}

### 2.2 Testing Methodology
Following industry standards:
- **OWASP Testing Guide v4.2** - Web application security testing
- **NIST SP 800-115** - Technical security testing and assessment
- **ISO/IEC 27001:2022** - Information security management

### 2.3 Tools and Techniques
- Automated vulnerability scanning (EMYUEL Scanner)
- Static code analysis
- Dynamic security testing
- Configuration review

### 2.4 Tools Deployment Summary
For each external security tool used, include a row in this table showing:
- Tool name, category, number of findings, and severity breakdown.
Use the FINDINGS BY TOOL data above for accuracy.

---

## 3. TOOL FINDINGS SUMMARY

For each security tool that produced findings, provide a brief summary:
- What the tool does
- What it found (count and severity level)
- Key findings from that tool

Group findings by source (AI Scanner vs External tools like Nmap, Nikto, SQLMap, etc.).

---

## 4. DETAILED FINDINGS

For each vulnerability discovered, provide detailed analysis using this format:

### 4.1 [SEVERITY] - [Vulnerability Title]

**Vulnerability ID:** VUL-{scan_id}-001  
**Discovered By:** [Tool name or AI Scanner]  
**CVSS Score:** [Calculate if applicable]  
**CWE ID:** [CWE classification if applicable]  
**OWASP Category:** [A01-A10 if web app]

#### Description
Detailed technical description of the vulnerability.

#### Location
- **File/URL:** [Exact location]
- **Line Number:** [If code]
- **Parameter:** [If applicable]

#### Impact Analysis
**Confidentiality:** [High/Medium/Low/None]  
**Integrity:** [High/Medium/Low/None]  
**Availability:** [High/Medium/Low/None]

Business impact explanation in non-technical terms.

#### Proof of Concept
```
[Technical evidence, code snippet, or reproduction steps]
```

#### Remediation Steps
1. **Immediate Fix:** [Quick fix if available]
2. **Proper Solution:** [Correct implementation]
3. **Verification:** [How to verify fix]

#### References
- OWASP: [Relevant guide]
- CWE: [Link if applicable]
- NIST: [Relevant publication]

---

[Repeat Section 4.X for each critical and high-severity finding]

---

## 5. RISK ASSESSMENT MATRIX

| Finding | Discovered By | Severity | Likelihood | Impact | Risk Level |
|---------|---------------|----------|------------|--------|------------|
| [Title] | [Tool]        | Critical | High       | High   | Critical   |
| ...     | ...           | ...      | ...        | ...    | ...        |

---

## 6. RECOMMENDATIONS

### 6.1 Critical Priority (Immediate Action Required)
1. **[Action]:** [Description]
   - Timeline: Within 24-48 hours
   - Owner: Security Team/DevOps
   
### 6.2 High Priority (Within 1 Week)
[List high-priority fixes]

### 6.3 Medium Priority (Within 1 Month)
[List medium-priority improvements]

### 6.4 Strategic Recommendations
Long-term security improvements:
- Security architecture enhancements
- Process improvements
- Security awareness training

---

## 7. COMPLIANCE CONSIDERATIONS

### 7.1 Regulatory Impact
- **GDPR:** [Impact if applicable]
- **PCI DSS:** [Impact if applicable]
- **HIPAA:** [Impact if applicable]
- **SOC 2:** [Impact if applicable]

### 7.2 Industry Standards
- ISO 27001:2022 compliance status
- NIST Cybersecurity Framework alignment

---

## 8. CONCLUSION

### 8.1 Summary
Overall assessment summary in 1-2 paragraphs.

### 8.2 Next Steps
1. Review and prioritize findings
2. Assign remediation tasks
3. Set target remediation dates
4. Schedule re-assessment

---

## APPENDIX A: VULNERABILITY STATISTICS

### Findings by Severity
- Critical: {severity.get('critical', 0)}
- High: {severity.get('high', 0)}
- Medium: {severity.get('medium', 0)}
- Low: {severity.get('low', 0)}

### Findings by Category
[Categorize by OWASP Top 10, CWE, etc.]

---

## APPENDIX B: TECHNICAL DETAILS

### Scan Configuration
- Scanner Version: EMYUEL v1.0
- Scan ID: {scan_id}
- Duration: {duration:.2f} seconds

### Coverage
- Pages Scanned: [Number]
- Endpoints Tested: [Number]
- Parameters Analyzed: [Number]

---

**Report Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Classification:** CONFIDENTIAL - For Internal Use Only

---

IMPORTANT FORMATTING GUIDELINES:
1. Use professional, technical language
2. Be specific and actionable
3. Include CVSS scores where applicable
4. Reference industry standards (OWASP, CWE, NIST)
5. Provide clear remediation steps
6. Focus on business impact, not just technical details
7. Use Markdown formatting for readability
8. Include severity-based prioritization
9. Follow the exact structure provided above
10. Make it audit-ready and compliance-focused
"""
        
        return prompt
    
    def _generate_fallback_report(self, results: Dict[str, Any]) -> str:
        """
        Generate template-based report if AI fails
        
        Args:
            results: Scan results dictionary
            
        Returns:
            Basic markdown report
        """
        logger.warning("Using fallback report template")
        
        target = results.get('target', 'Unknown')
        total = results.get('total_findings', 0)
        severity = results.get('findings_by_severity', {})
        findings = results.get('findings', [])
        
        report = f"""# VULNERABILITY ASSESSMENT REPORT

## EXECUTIVE SUMMARY

**Target:** {target}  
**Total Findings:** {total}  
**Risk Level:** {'Critical' if severity.get('critical', 0) > 0 else 'High' if severity.get('high', 0) > 0 else 'Medium'}

### Severity Distribution
- Critical: {severity.get('critical', 0)}
- High: {severity.get('high', 0)}
- Medium: {severity.get('medium', 0)}
- Low: {severity.get('low', 0)}

## DETAILED FINDINGS

"""
        
        # Per-tool summary
        tool_groups = {}
        for f in findings:
            tool_name = f.get('tool', f.get('source', 'AI Scanner'))
            if tool_name.startswith('external:'):
                tool_name = tool_name.replace('external:', '')
            if tool_name not in tool_groups:
                tool_groups[tool_name] = []
            tool_groups[tool_name].append(f)
        
        if tool_groups:
            report += "## TOOL FINDINGS SUMMARY\n\n"
            report += "| Tool | Findings | Severities |\n"
            report += "|------|----------|------------|\n"
            for tool_name, tool_findings in sorted(tool_groups.items(), key=lambda x: len(x[1]), reverse=True):
                sevs = {}
                for f in tool_findings:
                    s = f.get('severity', 'info').lower()
                    sevs[s] = sevs.get(s, 0) + 1
                sev_str = ', '.join(f"{k}: {v}" for k, v in sorted(sevs.items()))
                report += f"| {tool_name} | {len(tool_findings)} | {sev_str} |\n"
            report += "\n---\n\n"
        
        for i, finding in enumerate(findings, 1):
            tool_label = finding.get('tool', finding.get('source', ''))
            if tool_label.startswith('external:'):
                tool_label = tool_label.replace('external:', '')
            tool_tag = f" (by {tool_label})" if tool_label else ""
            report += f"""### {i}. [{finding.get('severity', 'Unknown').upper()}] {finding.get('title', 'Untitled')}{tool_tag}

**Location:** {finding.get('file_path', finding.get('url', 'N/A'))}  
**Type:** {finding.get('type', 'N/A')}  
**Tool:** {tool_label or 'AI Scanner'}

**Description:**  
{finding.get('description', 'No description available')}

---

"""
        
        report += f"""
## RECOMMENDATIONS

1. Address all Critical severity findings immediately
2. Prioritize High severity findings within 1 week
3. Review and fix Medium severity findings within 1 month
4. Implement security best practices

---

**Report Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        return report

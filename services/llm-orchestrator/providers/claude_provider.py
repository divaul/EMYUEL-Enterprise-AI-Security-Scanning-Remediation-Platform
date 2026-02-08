"""
Anthropic Claude Provider Implementation

Claude 3 based security analysis provider
"""

import json
import time
from typing import Dict, List, Any
from datetime import datetime
from anthropic import AsyncAnthropic, APIError, RateLimitError, AuthenticationError, APIConnectionError

from.base import (
    LLMProvider,
    ProviderType,
    AnalysisType,
    AnalysisResult,
    RemediationPatch,
    CVSSScore,
    ProviderUnavailableError,
    ProviderQuotaExceededError,
    ProviderAuthenticationError,
    ProviderInvalidResponseError
)


class ClaudeProvider(LLMProvider):
    """Anthropic Claude 3 provider implementation"""
    
    def __init__(self, api_key: str, model: str = "claude-3-opus-20240229", config: Dict[str, Any] = None):
        config = config or {}
        super().__init__(api_key, model, config)
        self.client = AsyncAnthropic(api_key=api_key)
        self.max_tokens = config.get('max_tokens', 4096)
        self.temperature = config.get('temperature', 0.1)
    
    def _get_provider_type(self) -> ProviderType:
        return ProviderType.CLAUDE
    
    async def _call_api(self, system_prompt: str, user_prompt: str) -> tuple:
        """Make API call to Claude"""
        start_time = time.time()
        
        try:
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_prompt}
                ]
            )
            
            processing_time = time.time() - start_time
            content = response.content[0].text
            tokens_used = response.usage.input_tokens + response.usage.output_tokens
            
            return content, tokens_used, processing_time
            
        except AuthenticationError as e:
            raise ProviderAuthenticationError(f"Claude authentication failed: {str(e)}")
        except RateLimitError as e:
            raise ProviderQuotaExceededError(f"Claude rate limit exceeded: {str(e)}")
        except APIConnectionError as e:
            raise ProviderUnavailableError(f"Claude connection failed: {str(e)}")
        except APIError as e:
            raise ProviderInvalidResponseError(f"Claude API error: {str(e)}")
        except Exception as e:
            raise ProviderInvalidResponseError(f"Unexpected Claude error: {str(e)}")
    
    async def analyze_code(
        self,
        code: str,
        context: Dict[str, Any],
        analysis_type: AnalysisType
    ) -> AnalysisResult:
        """Analyze code for security issues"""
        
        system_prompt = "You are an expert security researcher analyzing code for vulnerabilities. Always respond in valid JSON format only."
        
        user_prompt = f"""Perform {analysis_type.value} on the following code:

Code:
```
{code}
```

Context: {json.dumps(context, indent=2)}

Analyze thoroughly and respond in JSON format with the following structure:
{{
    "success": true,
    "findings": [
        {{
            "title": "Finding title",
            "description": "Detailed description",
            "severity": "critical/high/medium/low",
            "location": {{"file": "path", "line": 123}},
            "evidence": "Code evidence"
        }}
    ],
    "confidence_score": 0.95,
    "reasoning": "Your analysis reasoning"
}}

Respond with ONLY the JSON object, no additional text.
"""
        
        content, tokens, proc_time = await self._call_api(system_prompt, user_prompt)
        
        # Clean potential markdown formatting
        content = self._clean_json_response(content)
        
        try:
            result_data = json.loads(content)
        except json.JSONDecodeError as e:
            raise ProviderInvalidResponseError(f"Failed to parse JSON: {str(e)}\nContent: {content[:200]}")
        
        return AnalysisResult(
            success=result_data.get('success', True),
            analysis_type=analysis_type,
            findings=result_data.get('findings', []),
            confidence_score=result_data.get('confidence_score', 0.8),
            reasoning=result_data.get('reasoning', ''),
            provider=self.provider_type,
            model_used=self.model,
            tokens_used=tokens,
            processing_time=proc_time,
            timestamp=datetime.utcnow(),
            metadata=context
        )
    
    async def trace_data_flow(
        self,
        source_code: str,
        entry_points: List[str],
        dangerous_sinks: List[str],
        context: Dict[str, Any]
    ) -> AnalysisResult:
        """Trace data flow from source to sink"""
        
        system_prompt = "You are an expert in taint analysis and data flow security. Respond only in valid JSON format."
        
        user_prompt = f"""Analyze the following code for data flow from user input to dangerous operations.

Entry Points (Sources): {', '.join(entry_points)}
Dangerous Sinks: {', '.join(dangerous_sinks)}

Code:
```
{source_code}
```

Trace all data flow paths from entry points to dangerous sinks. For each path:
1. Identify the source (user input)
2. Track transformations and sanitization
3. Identify the sink (dangerous operation)
4. Assess exploitability

Respond with ONLY this JSON structure:
{{
    "success": true,
    "findings": [
        {{
            "path_id": "path_001",
            "source": "HTTP parameter 'user_id'",
            "sink": "SQL query execution",
            "flow_steps": ["step1: receives input", "step2: passes to function", "step3: used in query"],
            "sanitization": "none",
            "exploitable": true,
            "severity": "high",
            "attack_vector": "Detailed attack description"
        }}
    ],
    "confidence_score": 0.95,
    "reasoning": "Explanation of findings"
}}
"""
        
        content, tokens, proc_time = await self._call_api(system_prompt, user_prompt)
        content = self._clean_json_response(content)
        result_data = json.loads(content)
        
        return AnalysisResult(
            success=result_data.get('success', True),
            analysis_type=AnalysisType.DATA_FLOW,
            findings=result_data.get('findings', []),
            confidence_score=result_data.get('confidence_score', 0.8),
            reasoning=result_data.get('reasoning', ''),
            provider=self.provider_type,
            model_used=self.model,
            tokens_used=tokens,
            processing_time=proc_time,
            timestamp=datetime.utcnow(),
            metadata=context
        )
    
    async def detect_vulnerability(
        self,
        code: str,
        vulnerability_type: str,
        context: Dict[str, Any]
    ) -> AnalysisResult:
        """Detect specific vulnerability type"""
        
        vuln_prompts = {
            "sqli": "SQL injection vulnerabilities",
            "xss": "Cross-Site Scripting (XSS) vulnerabilities",
            "ssrf": "Server-Side Request Forgery (SSRF) vulnerabilities",
            "rce": "Remote Code Execution (RCE) vulnerabilities",
            "auth": "Authentication bypass vulnerabilities",
            "authz": "Authorization and privilege escalation vulnerabilities"
        }
        
        vuln_desc = vuln_prompts.get(vulnerability_type, f"{vulnerability_type} vulnerabilities")
        
        system_prompt = f"You are an expert in detecting {vuln_desc}. Respond only in valid JSON format."
        
        user_prompt = f"""Analyze the following code for {vuln_desc}.

Code:
```
{code}
```

Context: {json.dumps(context, indent=2)}

Identify all instances of {vuln_desc}. For each finding:
1. Exact location (file, line numbers)
2. Vulnerable code snippet
3. Attack vector description
4. Proof of concept
5. Severity assessment

Respond with ONLY valid JSON format with detailed findings.
"""
        
        content, tokens, proc_time = await self._call_api(system_prompt, user_prompt)
        content = self._clean_json_response(content)
        result_data = json.loads(content)
        
        return AnalysisResult(
            success=result_data.get('success', True),
            analysis_type=AnalysisType.VULNERABILITY_DETECTION,
            findings=result_data.get('findings', []),
            confidence_score=result_data.get('confidence_score', 0.8),
            reasoning=result_data.get('reasoning', ''),
            provider=self.provider_type,
            model_used=self.model,
            tokens_used=tokens,
            processing_time=proc_time,
            timestamp=datetime.utcnow(),
            metadata={"vulnerability_type": vulnerability_type, **context}
        )
    
    async def generate_remediation(
        self,
        vulnerability: Dict[str, Any]
    ) -> RemediationPatch:
        """Generate code-level remediation patch"""
        
        system_prompt = "You are an expert security engineer providing code remediation. Respond only in JSON."
        
        user_prompt = f"""Generate a remediation patch for the following vulnerability:

Vulnerability Details:
{json.dumps(vulnerability, indent=2)}

Provide:
1. Line-by-line explanation of the vulnerability
2. Secure alternative code
3. Explanation of the fix
4. Additional security recommendations

Respond with ONLY this JSON structure:
{{
    "original_code": "...",
    "patched_code": "...",
    "explanation": "...",
    "confidence": 0.95,
    "additional_recommendations": ["...", "..."]
}}
"""
        
        content, tokens, proc_time = await self._call_api(system_prompt, user_prompt)
        content = self._clean_json_response(content)
        result_data = json.loads(content)
        
        return RemediationPatch(
            vulnerability_id=vulnerability.get('id', 'unknown'),
            file_path=vulnerability.get('file_path', ''),
            line_start=vulnerability.get('line_start', 0),
            line_end=vulnerability.get('line_end', 0),
            original_code=result_data.get('original_code', ''),
            patched_code=result_data.get('patched_code', ''),
            explanation=result_data.get('explanation', ''),
            confidence=result_data.get('confidence', 0.8),
            provider=self.provider_type,
            metadata={'additional_recommendations': result_data.get('additional_recommendations', [])}
        )
    
    async def calculate_cvss(
        self,
        vulnerability: Dict[str, Any]
    ) -> CVSSScore:
        """Calculate CVSS v3 score"""
        
        system_prompt = "You are a CVSS v3 scoring expert. Respond only in JSON."
        
        user_prompt = f"""Calculate CVSS v3 score for the following vulnerability:

{json.dumps(vulnerability, indent=2)}

Provide complete CVSS v3 metrics and calculated base score.

Respond with ONLY valid JSON containing all metrics.
"""
        
        content, tokens, proc_time = await self._call_api(system_prompt, user_prompt)
        content = self._clean_json_response(content)
        result_data = json.loads(content)
        
        base_score = result_data.get('base_score', 0.0)
        severity = self._severity_from_score(base_score)
        
        return CVSSScore(
            base_score=base_score,
            vector_string=result_data.get('vector_string', ''),
            severity=severity,
            attack_vector=result_data.get('attack_vector', 'Unknown'),
            attack_complexity=result_data.get('attack_complexity', 'Unknown'),
            privileges_required=result_data.get('privileges_required', 'Unknown'),
            user_interaction=result_data.get('user_interaction', 'Unknown'),
            scope=result_data.get('scope', 'Unknown'),
            confidentiality_impact=result_data.get('confidentiality_impact', 'Unknown'),
            integrity_impact=result_data.get('integrity_impact', 'Unknown'),
            availability_impact=result_data.get('availability_impact', 'Unknown'),
            provider=self.provider_type,
            explanation=result_data.get('explanation', '')
        )
    
    async def health_check(self) -> bool:
        """Check provider availability"""
        try:
            await self.client.messages.create(
                model=self.model,
                max_tokens=10,
                messages=[{"role": "user", "content": "Hello"}]
            )
            return True
        except Exception:
            return False
    
    async def estimate_tokens(self, text: str) -> int:
        """Estimate token count"""
        # Claude uses similar tokenization to GPT
        return len(text) // 4
    
    def _clean_json_response(self, content: str) -> str:
        """Clean JSON from markdown formatting"""
        content = content.strip()
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        return content.strip()
    
    def _severity_from_score(self, score: float) -> str:
        """Convert CVSS score to severity level"""
        if score == 0.0:
            return "None"
        elif score < 4.0:
            return "Low"
        elif score < 7.0:
            return "Medium"
        elif score < 9.0:
            return "High"
        else:
            return "Critical"

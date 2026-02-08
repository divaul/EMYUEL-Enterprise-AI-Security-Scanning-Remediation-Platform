"""
OpenAI Provider Implementation

GPT-4 based security analysis provider
"""

import asyncio
import json
import time
from typing import Dict, List, Any
from datetime import datetime
import openai
from openai import AsyncOpenAI

from .base import (
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


class OpenAIProvider(LLMProvider):
    """OpenAI GPT-4 provider implementation"""
    
    def __init__(self, api_key: str, model: str = "gpt-4-turbo-preview", config: Dict[str, Any] = None):
        config = config or {}
        super().__init__(api_key, model, config)
        self.client = AsyncOpenAI(api_key=api_key)
        self.max_tokens = config.get('max_tokens', 4096)
        self.temperature = config.get('temperature', 0.1)
    
    def _get_provider_type(self) -> ProviderType:
        return ProviderType.OPENAI
    
    async def _call_api(self, messages: List[Dict[str, str]], response_format: str = "text") -> tuple:
        """Make API call to OpenAI"""
        start_time = time.time()
        
        try:
            kwargs = {
                "model": self.model,
                "messages": messages,
                "max_tokens": self.max_tokens,
                "temperature": self.temperature
            }
            
            # Add JSON mode if requested
            if response_format == "json":
                kwargs["response_format"] = {"type": "json_object"}
            
            response = await self.client.chat.completions.create(**kwargs)
            
            processing_time = time.time() - start_time
            content = response.choices[0].message.content
            tokens_used = response.usage.total_tokens
            
            return content, tokens_used, processing_time
            
        except openai.AuthenticationError as e:
            raise ProviderAuthenticationError(f"OpenAI authentication failed: {str(e)}")
        except openai.RateLimitError as e:
            raise ProviderQuotaExceededError(f"OpenAI rate limit exceeded: {str(e)}")
        except openai.APIConnectionError as e:
            raise ProviderUnavailableError(f"OpenAI connection failed: {str(e)}")
        except Exception as e:
            raise ProviderInvalidResponseError(f"OpenAI API error: {str(e)}")
    
    async def analyze_code(
        self,
        code: str,
        context: Dict[str, Any],
        analysis_type: AnalysisType
    ) -> AnalysisResult:
        """Analyze code for security issues"""
        
        prompt = self._build_analysis_prompt(code, context, analysis_type)
        messages = [
            {"role": "system", "content": "You are an expert security researcher analyzing code for vulnerabilities. Respond in JSON format."},
            {"role": "user", "content": prompt}
        ]
        
        content, tokens, proc_time = await self._call_api(messages, response_format="json")
        
        try:
            result_data = json.loads(content)
        except json.JSONDecodeError:
            raise ProviderInvalidResponseError("Failed to parse JSON response")
        
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
        
        prompt = f"""Analyze the following code for data flow from user input to dangerous operations.

Entry Points (Sources): {', '.join(entry_points)}
Dangerous Sinks: {', '.join(dangerous_sinks)}

Code:
```
{source_code}
```

Trace all data flow paths from entry points to dangerous sinks. For each path found:
1. Identify the source (user input)
2. Track transformations and sanitization
3. Identify the sink (dangerous operation)
4. Assess exploitability

Respond in JSON format:
{{
    "success": true,
    "findings": [
        {{
            "path_id": "path_001",
            "source": "HTTP parameter 'user_id'",
            "sink": "SQL query execution",
            "flow_steps": ["step1", "step2", ...],
            "sanitization": "none",
            "exploitable": true,
            "severity": "high"
        }}
    ],
    "confidence_score": 0.95,
    "reasoning": "Explanation of findings"
}}
"""
        
        messages = [
            {"role": "system", "content": "You are an expert in taint analysis and data flow security. Respond in JSON."},
            {"role": "user", "content": prompt}
        ]
        
        content, tokens, proc_time = await self._call_api(messages, response_format="json")
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
        
        prompt = f"""Analyze the following code for {vuln_desc}.

Code:
```
{code}
```

Context: {json.dumps(context, indent=2)}

Identify all instances of {vuln_desc}. For each finding:
1. Exact location (file, line numbers)
2. Vulnerable code snippet
3. Attack vector description
4. Proof of concept (if applicable)
5. Severity assessment

Respond in JSON format with detailed findings.
"""
        
        messages = [
            {"role": "system", "content": f"You are an expert in detecting {vuln_desc}. Respond in JSON."},
            {"role": "user", "content": prompt}
        ]
        
        content, tokens, proc_time = await self._call_api(messages, response_format="json")
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
        
        prompt = f"""Generate a remediation patch for the following vulnerability:

Vulnerability Details:
{json.dumps(vulnerability, indent=2)}

Provide:
1. Line-by-line explanation of the vulnerability
2. Secure alternative code
3. Explanation of the fix
4. Additional security recommendations

Respond in JSON format:
{{
    "original_code": "...",
    "patched_code": "...",
    "explanation": "...",
    "confidence": 0.95,
    "additional_recommendations": ["...", "..."]
}}
"""
        
        messages = [
            {"role": "system", "content": "You are an expert security engineer providing code remediation. Respond in JSON."},
            {"role": "user", "content": prompt}
        ]
        
        content, tokens, proc_time = await self._call_api(messages, response_format="json")
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
            metadata=result_data.get('additional_recommendations')
        )
    
    async def calculate_cvss(
        self,
        vulnerability: Dict[str, Any]
    ) -> CVSSScore:
        """Calculate CVSS v3 score"""
        
        prompt = f"""Calculate CVSS v3 score for the following vulnerability:

{json.dumps(vulnerability, indent=2)}

Provide complete CVSS v3 metrics:
- Attack Vector (Network/Adjacent/Local/Physical)
- Attack Complexity (Low/High)
- Privileges Required (None/Low/High)
- User Interaction (None/Required)
- Scope (Unchanged/Changed)
- Confidentiality Impact (None/Low/High)
- Integrity Impact (None/Low/High)
- Availability Impact (None/Low/High)

Respond in JSON format with all metrics and calculated base score.
"""
        
        messages = [
            {"role": "system", "content": "You are a CVSS scoring expert. Respond in JSON."},
            {"role": "user", "content": prompt}
        ]
        
        content, tokens, proc_time = await self._call_api(messages, response_format="json")
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
            messages = [{"role": "user", "content": "Hello"}]
            await asyncio.wait_for(
                self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    max_tokens=5
                ),
                timeout=10.0
            )
            return True
        except Exception:
            return False
    
    async def estimate_tokens(self, text: str) -> int:
        """Estimate token count (rough approximation)"""
        # Rough estimate: ~4 chars per token for English
        return len(text) // 4
    
    def _build_analysis_prompt(self, code: str, context: Dict[str, Any], analysis_type: AnalysisType) -> str:
        """Build prompt for general code analysis"""
        return f"""Perform {analysis_type.value} on the following code:

Code:
```
{code}
```

Context: {json.dumps(context, indent=2)}

Analyze thoroughly and respond in JSON format with findings, confidence score, and reasoning.
"""
    
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

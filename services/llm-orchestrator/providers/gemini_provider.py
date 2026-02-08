"""
Google Gemini Provider Implementation

Gemini Pro based security analysis provider
"""

import json
import time
from typing import Dict, List, Any
from datetime import datetime
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

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


class GeminiProvider(LLMProvider):
    """Google Gemini Pro provider implementation"""
    
    def __init__(self, api_key: str, model: str = "gemini-pro", config: Dict[str, Any] = None):
        config = config or {}
        super().__init__(api_key, model, config)
        
        genai.configure(api_key=api_key)
        
        # Configure safety settings to allow security content
        self.safety_settings = {
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
        }
        
        generation_config = {
            "temperature": config.get('temperature', 0.1),
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": config.get('max_tokens', 4096),
        }
        
        self.model_instance = genai.GenerativeModel(
            model_name=model,
            generation_config=generation_config,
            safety_settings=self.safety_settings
        )
    
    def _get_provider_type(self) -> ProviderType:
        return ProviderType.GEMINI
    
    async def _call_api(self, prompt: str) -> tuple:
        """Make API call to Gemini"""
        start_time = time.time()
        
        try:
            response = await self.model_instance.generate_content_async(prompt)
            processing_time = time.time() - start_time
            
            if not response.text:
                raise ProviderInvalidResponseError("Empty response from Gemini")
            
            content = response.text
            # Gemini doesn't provide token count in same way, estimate
            tokens_used = len(prompt) // 4 + len(content) // 4
            
            return content, tokens_used, processing_time
            
        except Exception as e:
            error_str = str(e).lower()
            if "api key" in error_str or "authentication" in error_str:
                raise ProviderAuthenticationError(f"Gemini authentication failed: {str(e)}")
            elif "quota" in error_str or "rate limit" in error_str:
                raise ProviderQuotaExceededError(f"Gemini quota exceeded: {str(e)}")
            elif "connection" in error_str or "network" in error_str:
                raise ProviderUnavailableError(f"Gemini connection failed: {str(e)}")
            else:
                raise ProviderInvalidResponseError(f"Gemini API error: {str(e)}")
    
    async def analyze_code(
        self,
        code: str,
        context: Dict[str, Any],
        analysis_type: AnalysisType
    ) -> AnalysisResult:
        """Analyze code for security issues"""
        
        prompt = f"""You are an expert security researcher analyzing code for vulnerabilities.

Perform {analysis_type.value} on the following code:

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
            "severity": "high/medium/low",
            "location": {{"file": "path", "line": 123}},
            "evidence": "Code evidence"
        }}
    ],
    "confidence_score": 0.95,
    "reasoning": "Your analysis reasoning"
}}

IMPORTANT: Respond ONLY with valid JSON, no additional text.
"""
        
        content, tokens, proc_time = await self._call_api(prompt)
        
        # Extract JSON from response (Gemini sometimes adds markdown)
        content = content.strip()
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()
        
        try:
            result_data = json.loads(content)
        except json.JSONDecodeError as e:
            raise ProviderInvalidResponseError(f"Failed to parse JSON response: {str(e)}\nContent: {content[:200]}")
        
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
        
        prompt = f"""You are an expert in taint analysis and data flow security.

Analyze the following code for data flow from user input to dangerous operations.

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

Respond ONLY with valid JSON:
{{
    "success": true,
    "findings": [
        {{
            "path_id": "path_001",
            "source": "HTTP parameter 'user_id'",
            "sink": "SQL query execution",
            "flow_steps": ["step1", "step2"],
            "sanitization": "none",
            "exploitable": true,
            "severity": "high"
        }}
    ],
    "confidence_score": 0.95,
    "reasoning": "Explanation of findings"
}}
"""
        
        content, tokens, proc_time = await self._call_api(prompt)
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
        
        prompt = f"""You are an expert in detecting {vuln_desc}.

Analyze the following code for {vuln_desc}.

Code:
```
{code}
```

Context: {json.dumps(context, indent=2)}

Identify all instances. Respond ONLY with valid JSON format with detailed findings.
"""
        
        content, tokens, proc_time = await self._call_api(prompt)
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
        
        prompt = f"""You are an expert security engineer providing code remediation.

Generate a remediation patch for the following vulnerability:

{json.dumps(vulnerability, indent=2)}

Respond ONLY with valid JSON:
{{
    "original_code": "...",
    "patched_code": "...",
    "explanation": "...",
    "confidence": 0.95
}}
"""
        
        content, tokens, proc_time = await self._call_api(prompt)
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
            provider=self.provider_type
        )
    
    async def calculate_cvss(
        self,
        vulnerability: Dict[str, Any]
    ) -> CVSSScore:
        """Calculate CVSS v3 score"""
        
        prompt = f"""You are a CVSS v3 scoring expert.

Calculate CVSS v3 score for:
{json.dumps(vulnerability, indent=2)}

Respond ONLY with valid JSON containing all CVSS v3 metrics and calculated base score.
"""
        
        content, tokens, proc_time = await self._call_api(prompt)
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
            await self.model_instance.generate_content_async("Hello")
            return True
        except Exception:
            return False
    
    async def estimate_tokens(self, text: str) -> int:
        """Estimate token count"""
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

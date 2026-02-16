"""
LLM Analyzer - Use LLM for intelligent vulnerability analysis

Supports OpenAI, Google Gemini, and Anthropic Claude
"""

import json
import re
from typing import Dict, Any, List, Optional
import asyncio


class LLMAnalyzer:
    """Analyze code and web responses using LLM for vulnerability detection"""
    
    def __init__(self, api_key_manager, provider='openai'):
        """
        Initialize LLM analyzer
        
        Args:
            api_key_manager: API key manager instance
            provider: LLM provider (openai, gemini, claude)
        """
        self.api_keys = api_key_manager
        self.provider = provider
        self.usage_stats = {
            'total_requests': 0,
            'total_tokens': 0,
            'errors': 0
        }
    
    async def analyze_code(self, code: str, file_path: str, language: str = 'python') -> List[Dict[str, Any]]:
        """
        Analyze code for security vulnerabilities
        
        Args:
            code: Source code to analyze
            file_path: Path to the file
            language: Programming language
            
        Returns:
            List of vulnerability findings
        """
        # Skip if code is too short
        if len(code.strip()) < 50:
            return []
        
        # Truncate if too long (to avoid token limits)
        max_code_length = 4000
        if len(code) > max_code_length:
            code = code[:max_code_length] + "\n... (truncated)"
        
        prompt = self._build_code_analysis_prompt(code, file_path, language)
        
        try:
            response = await self._call_llm(prompt)
            vulnerabilities = self._parse_vulnerabilities_from_response(response, file_path)
            
            self.usage_stats['total_requests'] += 1
            
            return vulnerabilities
            
        except Exception as e:
            self.usage_stats['errors'] += 1
            print(f"[LLM Error] {str(e)}")
            return []
    
    async def analyze_web_response(self, url: str, method: str, response_data: Dict) -> List[Dict[str, Any]]:
        """
        Analyze HTTP response for security issues
        
        Args:
            url: Request URL
            method: HTTP method
            response_data: Response data (headers, body, status)
            
        Returns:
            List of vulnerability findings
        """
        prompt = self._build_web_analysis_prompt(url, method, response_data)
        
        try:
            response = await self._call_llm(prompt)
            vulnerabilities = self._parse_vulnerabilities_from_response(response, url)
            
            self.usage_stats['total_requests'] += 1
            
            return vulnerabilities
            
        except Exception as e:
            self.usage_stats['errors'] += 1
            print(f"[LLM Error] {str(e)}")
            return []
    
    def _build_code_analysis_prompt(self, code: str, file_path: str, language: str) -> str:
        """Build prompt for code analysis"""
        return f"""You are an expert security auditor. Analyze this code for vulnerabilities.

File: {file_path}
Language: {language}

Code:
```{language}
{code}
```

Find security vulnerabilities including but not limited to:
- SQL Injection
- Cross-Site Scripting (XSS)
- Remote Code Execution (RCE)
- Path Traversal
- Insecure Deserialization
- Authentication/Authorization flaws
- Hardcoded secrets (API keys, passwords)
- Insecure cryptography
- SSRF (Server-Side Request Forgery)

Respond ONLY with valid JSON in this exact format (no markdown, no extra text):
{{
  "vulnerabilities": [
    {{
      "type": "sqli",
      "severity": "high",
      "line": 42,
      "description": "SQL injection vulnerability due to unsanitized user input",
      "evidence": "query = 'SELECT * FROM users WHERE id=' + user_id",
      "remediation": "Use parameterized queries or ORM"
    }}
  ]
}}

If no vulnerabilities found, return: {{"vulnerabilities": []}}
"""
    
    def _build_web_analysis_prompt(self, url: str, method: str, response_data: Dict) -> str:
        """Build prompt for web response analysis"""
        headers = response_data.get('headers', {})
        body_preview = response_data.get('body', '')[:1000]
        status = response_data.get('status', 200)
        
        return f"""You are a web security expert. Analyze this HTTP response for vulnerabilities.

URL: {url}
Method: {method}
Status: {status}

Response Headers:
{json.dumps(headers, indent=2)}

Response Body (preview):
{body_preview}

Check for:
- Missing security headers (CSP, X-Frame-Options, etc.)
- XSS vulnerabilities in response
- Information disclosure
- Insecure cookies
- CORS misconfigurations
- Sensitive data exposure

Respond ONLY with valid JSON (no markdown):
{{
  "vulnerabilities": [
    {{
      "type": "xss",
      "severity": "high",
      "description": "Reflected XSS in search parameter",
      "evidence": "User input reflected without encoding",
      "remediation": "Sanitize and encode all user inputs"
    }}
  ]
}}

If no vulnerabilities: {{"vulnerabilities": []}}
"""
    
    async def _call_llm(self, prompt: str) -> str:
        """Call LLM API based on provider"""
        if self.provider == 'openai':
            return await self._call_openai(prompt)
        elif self.provider == 'gemini':
            return await self._call_gemini(prompt)
        elif self.provider == 'claude':
            return await self._call_claude(prompt)
        else:
            raise ValueError(f"Unknown provider: {self.provider}")
    
    async def _call_openai(self, prompt: str) ->str:
        """Call OpenAI API"""
        try:
            from openai import OpenAI
        except ImportError:
            raise ImportError("openai package not installed. Run: pip install openai")
        
        api_key = self.api_keys.get_key('openai')
        if not api_key:
            raise ValueError("OpenAI API key not configured")
        
        client = OpenAI(api_key=api_key)
        
        try:
            response = await asyncio.to_thread(
                client.chat.completions.create,
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a security expert. Respond only with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=2000
            )
            
            content = response.choices[0].message.content
            self.usage_stats['total_tokens'] += response.usage.total_tokens
            
            return content
            
        except Exception as e:
            # Fallback to gpt-3.5-turbo if gpt-4 fails
            try:
                response = await asyncio.to_thread(
                    client.chat.completions.create,
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a security expert. Respond only with valid JSON."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.1,
                    max_tokens=2000
                )
                
                content = response.choices[0].message.content
                self.usage_stats['total_tokens'] += response.usage.total_tokens
                
                return content
            except:
                raise e
    
    async def _call_gemini(self, prompt: str) -> str:
        """Call Google Gemini API"""
        try:
            import google.generativeai as genai
        except ImportError:
            raise ImportError("google-generativeai package not installed. Run: pip install google-generativeai")
        
        api_key = self.api_keys.get_key('gemini')
        if not api_key:
            raise ValueError("Gemini API key not configured")
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro')
        
        response = await asyncio.to_thread(
            model.generate_content,
            prompt
        )
        
        return response.text
    
    async def _call_claude(self, prompt: str) -> str:
        """Call Anthropic Claude API"""
        try:
            import anthropic
        except ImportError:
            raise ImportError("anthropic package not installed. Run: pip install anthropic")
        
        api_key = self.api_keys.get_key('claude')
        if not api_key:
            raise ValueError("Claude API key not configured")
        
        client = anthropic.Anthropic(api_key=api_key)
        
        response = await asyncio.to_thread(
            client.messages.create,
            model="claude-3-sonnet-20240229",
            max_tokens=2000,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        return response.content[0].text
    
    def _parse_vulnerabilities_from_response(self, response: str, context: str) -> List[Dict[str, Any]]:
        """Parse vulnerability findings from LLM response"""
        # Remove markdown code blocks if present
        response = re.sub(r'```json\s*', '', response)
        response = re.sub(r'```\s*', '', response)
        response = response.strip()
        
        try:
            data = json.loads(response)
            vulnerabilities = data.get('vulnerabilities', [])
            
            # Add context to each finding
            for vuln in vulnerabilities:
                vuln['source'] = 'llm'
                vuln['context'] = context
                vuln['confidence'] = 0.8  # LLM-based findings have high confidence
                
                # Normalize severity
                severity = vuln.get('severity', 'medium').lower()
                if severity not in ['critical', 'high', 'medium', 'low']:
                    vuln['severity'] = 'medium'
            
            return vulnerabilities
            
        except json.JSONDecodeError as e:
            print(f"[LLM] Failed to parse JSON response: {e}")
            print(f"[LLM] Response was: {response[:200]}")
            return []
    
    async def chat(self, prompt: str) -> str:
        """
        General-purpose chat/completion method for LLM interaction
        
        This method provides a simple interface for getting responses from LLM
        without needing to structure them as vulnerability findings.
        
        Args:
            prompt: Text prompt for the LLM
            
        Returns:
            LLM response as string
            
        Raises:
            ValueError: If API key is not configured
            Exception: If API call fails
            
        Example:
            >>> llm = LLMAnalyzer(api_mgr, 'gemini')
            >>> response = await llm.chat("Explain SQL injection in one sentence")
            >>> print(response)
        """
        try:
            response = await self._call_llm(prompt)
            self.usage_stats['total_requests'] += 1
            return response
        except Exception as e:
            self.usage_stats['errors'] += 1
            raise Exception(f"LLM chat failed: {str(e)}")
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get LLM usage statistics"""
        return self.usage_stats.copy()

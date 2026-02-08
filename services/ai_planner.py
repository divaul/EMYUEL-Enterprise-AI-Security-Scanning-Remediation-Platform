"""
AI Planner - Intelligent Security Testing Strategy Generator

This module uses LLM to analyze security targets and generate
dynamic, adaptive testing strategies.
"""

import asyncio
import aiohttp
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum
import openai
from pathlib import Path


class TargetType(Enum):
    """Types of security targets"""
    STATIC_WEBSITE = "static_website"
    DYNAMIC_WEB_APP = "dynamic_web_app"
    REST_API = "rest_api"
    LOGIN_PAGE = "login_page"
    ADMIN_PANEL = "admin_panel"
    CMS = "cms"
    E_COMMERCE = "e_commerce"
    UNKNOWN = "unknown"


class RiskLevel(Enum):
    """Risk assessment levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class TargetAnalysis:
    """Results from initial target analysis"""
    url: str
    target_type: TargetType
    technologies: List[str]
    attack_surface: Dict[str, str]
    risk_level: RiskLevel
    recommended_strategy: str
    response_time: float
    http_status: int
    headers: Dict[str, str]
    
    def to_dict(self):
        return {
            **asdict(self),
            'target_type': self.target_type.value,
            'risk_level': self.risk_level.value
        }


@dataclass
class TestStep:
    """Individual test step in the plan"""
    step_number: int
    name: str
    objective: str
    method: str
    tool: str
    params: Dict[str, Any]
    risk_level: RiskLevel
    estimated_time: int  # seconds
    requires_approval: bool
    
    def to_dict(self):
        return {
            **asdict(self),
            'risk_level': self.risk_level.value
        }


@dataclass
class TestPlan:
    """Complete testing plan"""
    target_url: str
    total_steps: int
    steps: List[TestStep]
    strategy: str
    estimated_duration: int
    created_at: str
    
    def to_dict(self):
        return {
            **asdict(self),
            'steps': [step.to_dict() for step in self.steps]
        }


class NextAction(Enum):
    """What to do after reviewing step results"""
    CONTINUE = "continue"
    ADJUST_STRATEGY = "adjust_strategy"
    SKIP_REMAINING = "skip_remaining"
    STOP = "stop"
    ADD_STEPS = "add_steps"


@dataclass
class StepReview:
    """AI review of step results"""
    step_number: int
    success: bool
    findings: List[str]
    next_action: NextAction
    reasoning: str
    new_steps: Optional[List[TestStep]] = None
    
    def to_dict(self):
        result = {
            **asdict(self),
            'next_action': self.next_action.value
        }
        if self.new_steps:
            result['new_steps'] = [step.to_dict() for step in self.new_steps]
        return result


class AIPlanner:
    """
    AI-powered security testing planner
    
    Uses LLM to analyze targets and generate intelligent,
    adaptive testing strategies.
    """
    
    def __init__(self, api_key: str, model: str = "gpt-4", temperature: float = 0.3):
        """
        Initialize AI Planner
        
        Args:
            api_key: OpenAI API key
            model: LLM model to use
            temperature: LLM temperature (lower = more deterministic)
        """
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        openai.api_key = api_key
        
        # Stats
        self.analyses_performed = 0
        self.plans_generated = 0
    
    async def analyze_target(self, url: str) -> TargetAnalysis:
        """
        Perform initial analysis of the target
        
        Steps:
        1. Make HTTP request to target
        2. Analyze response (headers, content, response time)
        3. Detect technologies
        4. Use LLM to classify target type and assess risk
        
        Args:
            url: Target URL to analyze
            
        Returns:
            TargetAnalysis with comprehensive assessment
        """
        print(f"[AI PLANNER] Analyzing target: {url}")
        
        # Step 1: HTTP Request
        start_time = datetime.now()
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    status = response.status
                    headers = dict(response.headers)
                    content = await response.text()
                    response_time = (datetime.now() - start_time).total_seconds()
            except Exception as e:
                print(f"[AI PLANNER] Error fetching target: {e}")
                # Return minimal analysis
                return TargetAnalysis(
                    url=url,
                    target_type=TargetType.UNKNOWN,
                    technologies=[],
                    attack_surface={},
                    risk_level=RiskLevel.MEDIUM,
                    recommended_strategy="Unable to connect to target",
                    response_time=0,
                    http_status=0,
                    headers={}
                )
        
        # Step 2: Technology Detection (simple)
        technologies = self._detect_technologies(headers, content)
        
        # Step 3: LLM Analysis
        analysis = await self._llm_analyze_target(
            url=url,
            status=status,
            headers=headers,
            content_snippet=content[:2000],  # First 2000 chars
            technologies=technologies,
            response_time=response_time
        )
        
        self.analyses_performed += 1
        
        print(f"[AI PLANNER] Analysis complete: {analysis.target_type.value}")
        return analysis
    
    def _detect_technologies(self, headers: Dict, content: str) -> List[str]:
        """Simple technology detection from headers and content"""
        technologies = []
        
        # Server header
        if 'Server' in headers:
            technologies.append(headers['Server'])
        
        # X-Powered-By
        if 'X-Powered-By' in headers:
            technologies.append(headers['X-Powered-By'])
        
        # Content-based detection
        content_lower = content.lower()
        if 'wordpress' in content_lower or 'wp-content' in content_lower:
            technologies.append('WordPress')
        if 'joomla' in content_lower:
            technologies.append('Joomla')
        if 'drupal' in content_lower:
            technologies.append('Drupal')
        if 'react' in content_lower:
            technologies.append('React')
        if 'vue' in content_lower:
            technologies.append('Vue.js')
        if 'angular' in content_lower:
            technologies.append('Angular')
        
        return technologies
    
    async def _llm_analyze_target(self, url: str, status: int, headers: Dict, 
                                    content_snippet: str, technologies: List[str],
                                    response_time: float) -> TargetAnalysis:
        """Use LLM to analyze target and classify"""
        
        prompt = f"""You are an expert penetration tester analyzing a security target.

Target URL: {url}
HTTP Status: {status}
Response Time: {response_time:.2f}s
Detected Technologies: {', '.join(technologies) if technologies else 'None'}
Headers: {json.dumps({k: v for k, v in headers.items() if k in ['Server', 'X-Powered-By', 'X-Frame-Options', 'Content-Security-Policy']}, indent=2)}
Content Preview (first 2000 chars):
{content_snippet}

Analyze this target and determine:
1. Target type: static_website, dynamic_web_app, rest_api, login_page, admin_panel, cms, e_commerce, or unknown
2. Primary attack vectors (e.g., authentication, input_validation, session_management)
3. Initial risk assessment: low, medium, high, or critical
4. Recommended testing strategy (1 sentence)

Respond ONLY with valid JSON in this exact format:
{{
  "target_type": "...",
  "attack_surface": {{
    "primary_vector": "priority_level"
  }},
  "risk_level": "...",
  "recommended_strategy": "..."
}}"""

        try:
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: openai.ChatCompletion.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are an expert penetration tester. Respond only with valid JSON."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=self.temperature,
                    max_tokens=500
                )
            )
            
            result = json.loads(response.choices[0].message.content)
            
            return TargetAnalysis(
                url=url,
                target_type=TargetType(result.get('target_type', 'unknown')),
                technologies=technologies,
                attack_surface=result.get('attack_surface', {}),
                risk_level=RiskLevel(result.get('risk_level', 'medium')),
                recommended_strategy=result.get('recommended_strategy', ''),
                response_time=response_time,
                http_status=status,
                headers=headers
            )
        
        except Exception as e:
            print(f"[AI PLANNER] LLM analysis error: {e}")
            # Fallback to heuristic analysis
            return TargetAnalysis(
                url=url,
                target_type=self._heuristic_classify(url, content_snippet),
                technologies=technologies,
                attack_surface={"general": "medium_priority"},
                risk_level=RiskLevel.MEDIUM,
                recommended_strategy="Perform comprehensive security scan",
                response_time=response_time,
                http_status=status,
                headers=headers
            )
    
    def _heuristic_classify(self, url: str, content: str) -> TargetType:
        """Fallback heuristic classification without LLM"""
        url_lower = url.lower()
        content_lower = content.lower()
        
        if 'login' in url_lower or 'signin' in url_lower:
            return TargetType.LOGIN_PAGE
        if 'admin' in url_lower:
            return TargetType.ADMIN_PANEL
        if 'api' in url_lower or 'rest' in url_lower:
            return TargetType.REST_API
        if 'wordpress' in content_lower or 'wp-' in content_lower:
            return TargetType.CMS
        if any(tag in content_lower for tag in ['<form', '<input', '<button']):
            return TargetType.DYNAMIC_WEB_APP
        
        return TargetType.STATIC_WEBSITE
    
    async def generate_test_plan(self, analysis: TargetAnalysis) -> TestPlan:
        """
        Generate intelligent test plan based on target analysis
        
        Uses LLM to create step-by-step testing strategy
        
        Args:
            analysis: TargetAnalysis from analyze_target()
            
        Returns:
            TestPlan with ordered steps
        """
        print(f"[AI PLANNER] Generating test plan for {analysis.target_type.value}...")
        
        prompt = f"""Based on this security target analysis, create a detailed penetration testing plan.

Target Analysis:
- URL: {analysis.url}
- Type: {analysis.target_type.value}
- Technologies: {', '.join(analysis.technologies)}
- Attack Surface: {json.dumps(analysis.attack_surface, indent=2)}
- Risk Level: {analysis.risk_level.value}
- Strategy: {analysis.recommended_strategy}

Generate 3-7 specific testing steps. For each step provide:
- name: Clear, specific name
- objective: What we're trying to find
- method: Specific technique (e.g., "brute_force_common_credentials", "sql_injection_scan")
- tool: Which tool to use (BruteForceDetector, SQLInjectionDetector, XSSDetector, etc.)
- params: JSON object with parameters
- risk_level: low, medium, high, or critical
- estimated_time: seconds
- requires_approval: true/false

Respond ONLY with valid JSON array of steps:
[
  {{
    "name": "...",
    "objective": "...",
    "method": "...",
    "tool": "...",
    "params": {{}},
    "risk_level": "...",
    "estimated_time": 60,
    "requires_approval": false
  }}
]"""

        try:
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: openai.ChatCompletion.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are an expert penetration tester. Respond only with valid JSON array."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=self.temperature,
                    max_tokens=1500
                )
            )
            
            steps_data = json.loads(response.choices[0].message.content)
            
            steps = []
            for i, step_data in enumerate(steps_data, 1):
                steps.append(TestStep(
                    step_number=i,
                    name=step_data['name'],
                    objective=step_data['objective'],
                    method=step_data['method'],
                    tool=step_data['tool'],
                    params=step_data.get('params', {}),
                    risk_level=RiskLevel(step_data.get('risk_level', 'medium')),
                    estimated_time=step_data.get('estimated_time', 60),
                    requires_approval=step_data.get('requires_approval', False)
                ))
            
            total_time = sum(step.estimated_time for step in steps)
            
            plan = TestPlan(
                target_url=analysis.url,
                total_steps=len(steps),
                steps=steps,
                strategy=analysis.recommended_strategy,
                estimated_duration=total_time,
                created_at=datetime.now().isoformat()
            )
            
            self.plans_generated += 1
            
            print(f"[AI PLANNER] Generated plan with {len(steps)} steps")
            return plan
        
        except Exception as e:
            print(f"[AI PLANNER] Plan generation error: {e}")
            # Fallback to basic plan
            return self._generate_fallback_plan(analysis)
    
    def _generate_fallback_plan(self, analysis: TargetAnalysis) -> TestPlan:
        """Generate basic plan without LLM"""
        steps = [
            TestStep(
                step_number=1,
                name="Security Headers Analysis",
                objective="Check for missing security headers",
                method="analyze_headers",
                tool="HeaderAnalyzer",
                params={},
                risk_level=RiskLevel.LOW,
                estimated_time=30,
                requires_approval=False
            ),
            TestStep(
                step_number=2,
                name="XSS Vulnerability Scan",
                objective="Test for cross-site scripting",
                method="xss_scan",
                tool="XSSDetector",
                params={},
                risk_level=RiskLevel.MEDIUM,
                estimated_time=120,
                requires_approval=False
            )
        ]
        
        return TestPlan(
            target_url=analysis.url,
            total_steps=len(steps),
            steps=steps,
            strategy="Basic security scan",
            estimated_duration=150,
            created_at=datetime.now().isoformat()
        )
    
    async def review_step_results(self, step: TestStep, results: Dict[str, Any]) -> StepReview:
        """
        Review results from a completed step and decide next action
        
        Args:
            step: The completed test step
            results: Results data from executor
            
        Returns:
            StepReview with AI decision
        """
        print(f"[AI PLANNER] Reviewing step {step.step_number}: {step.name}")
        
        prompt = f"""Review the results from this penetration testing step:

Step: {step.name}
Objective: {step.objective}
Method: {step.method}

Results:
{json.dumps(results, indent=2)}

Analyze:
1. Was this step successful?
2. What did we learn?
3. Should we: continue, adjust_strategy, skip_remaining, stop, or add_steps?
4. Why?

Respond ONLY with valid JSON:
{{
  "success": true/false,
  "findings": ["finding1", "finding2"],
  "next_action": "continue/adjust_strategy/skip_remaining/stop/add_steps",
  "reasoning": "explanation"
}}"""

        try:
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: openai.ChatCompletion.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are an expert penetration tester reviewing test results."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=self.temperature,
                    max_tokens=500
                )
            )
            
            review_data = json.loads(response.choices[0].message.content)
            
            return StepReview(
                step_number=step.step_number,
                success=review_data.get('success', False),
                findings=review_data.get('findings', []),
                next_action=NextAction(review_data.get('next_action', 'continue')),
                reasoning=review_data.get('reasoning', ''),
                new_steps=None  # TODO: Parse if add_steps
            )
        
        except Exception as e:
            print(f"[AI PLANNER] Review error: {e}")
            # Fallback: continue by default
            return StepReview(
                step_number=step.step_number,
                success=True,
                findings=["Step completed"],
                next_action=NextAction.CONTINUE,
                reasoning="Automatic review - continue testing"
            )


# Example usage
if __name__ == '__main__':
    async def test_planner():
        # Requires OpenAI API key
        api_key = "sk-..."  # Replace with actual key
        planner = AIPlanner(api_key)
        
        # Analyze target
        analysis = await planner.analyze_target("https://testphp.vulnweb.com")
        print(f"\nAnalysis: {analysis.to_dict()}")
        
        # Generate plan
        plan = await planner.generate_test_plan(analysis)
        print(f"\nPlan: {plan.to_dict()}")
    
    # asyncio.run(test_planner())
    print("AI Planner module loaded")

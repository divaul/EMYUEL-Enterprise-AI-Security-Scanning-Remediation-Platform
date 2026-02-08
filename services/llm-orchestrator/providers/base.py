"""
LLM Provider Base Class - Abstract interface for all LLM providers

This module defines the contract that all LLM providers must implement.
It ensures provider-agnostic behavior across OpenAI, Gemini, and Claude.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
from datetime import datetime


class ProviderType(Enum):
    """Supported LLM provider types"""
    OPENAI = "openai"
    GEMINI = "gemini"
    CLAUDE = "claude"


class AnalysisType(Enum):
    """Types of security analysis"""
    DATA_FLOW = "data_flow"
    STATIC_ANALYSIS = "static_analysis"
    VULNERABILITY_DETECTION = "vulnerability_detection"
    CODE_REVIEW = "code_review"
    REMEDIATION_GENERATION = "remediation_generation"
    CVSS_SCORING = "cvss_scoring"


@dataclass
class AnalysisResult:
    """Result from LLM analysis"""
    success: bool
    analysis_type: AnalysisType
    findings: List[Dict[str, Any]]
    confidence_score: float
    reasoning: str
    provider: ProviderType
    model_used: str
    tokens_used: int
    processing_time: float
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "success": self.success,
            "analysis_type": self.analysis_type.value,
            "findings": self.findings,
            "confidence_score": self.confidence_score,
            "reasoning": self.reasoning,
            "provider": self.provider.value,
            "model_used": self.model_used,
            "tokens_used": self.tokens_used,
            "processing_time": self.processing_time,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata or {}
        }


@dataclass
class RemediationPatch:
    """Code remediation suggestion"""
    vulnerability_id: str
    file_path: str
    line_start: int
    line_end: int
    original_code: str
    patched_code: str
    explanation: str
    confidence: float
    provider: ProviderType
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "vulnerability_id": self.vulnerability_id,
            "file_path": self.file_path,
            "line_start": self.line_start,
            "line_end": self.line_end,
            "original_code": self.original_code,
            "patched_code": self.patched_code,
            "explanation": self.explanation,
            "confidence": self.confidence,
            "provider": self.provider.value,
            "metadata": self.metadata or {}
        }


@dataclass
class CVSSScore:
    """CVSS v3 vulnerability score"""
    base_score: float
    vector_string: str
    severity: str  # None, Low, Medium, High, Critical
    
    # Base Metrics
    attack_vector: str
    attack_complexity: str
    privileges_required: str
    user_interaction: str
    scope: str
    confidentiality_impact: str
    integrity_impact: str
    availability_impact: str
    
    # Metadata
    provider: ProviderType
    explanation: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "base_score": self.base_score,
            "vector_string": self.vector_string,
            "severity": self.severity,
            "attack_vector": self.attack_vector,
            "attack_complexity": self.attack_complexity,
            "privileges_required": self.privileges_required,
            "user_interaction": self.user_interaction,
            "scope": self.scope,
            "confidentiality_impact": self.confidentiality_impact,
            "integrity_impact": self.integrity_impact,
            "availability_impact": self.availability_impact,
            "provider": self.provider.value,
            "explanation": self.explanation
        }


class LLMProvider(ABC):
    """
    Abstract base class for all LLM providers.
    
    All provider implementations (OpenAI, Gemini, Claude) must inherit
    from this class and implement all abstract methods.
    """
    
    def __init__(self, api_key: str, model: str, config: Dict[str, Any]):
        """
        Initialize provider
        
        Args:
            api_key: API key for the provider
            model: Model identifier (e.g., 'gpt-4-turbo-preview')
            config: Additional configuration options
        """
        self.api_key = api_key
        self.model = model
        self.config = config
        self.provider_type = self._get_provider_type()
    
    @abstractmethod
    def _get_provider_type(self) -> ProviderType:
        """Return the provider type enum"""
        pass
    
    @abstractmethod
    async def analyze_code(
        self,
        code: str,
        context: Dict[str, Any],
        analysis_type: AnalysisType
    ) -> AnalysisResult:
        """
        Analyze code for security issues
        
        Args:
            code: Source code to analyze
            context: Additional context (file path, language, dependencies, etc.)
            analysis_type: Type of analysis to perform
            
        Returns:
            AnalysisResult with findings
        """
        pass
    
    @abstractmethod
    async def trace_data_flow(
        self,
        source_code: str,
        entry_points: List[str],
        dangerous_sinks: List[str],
        context: Dict[str, Any]
    ) -> AnalysisResult:
        """
        Trace data flow from user input (source) to dangerous operation (sink)
        
        Args:
            source_code: Full source code to analyze
            entry_points: List of user input entry points
            dangerous_sinks: List of dangerous operations to check
            context: Additional context
            
        Returns:
            AnalysisResult with data flow paths
        """
        pass
    
    @abstractmethod
    async def detect_vulnerability(
        self,
        code: str,
        vulnerability_type: str,
        context: Dict[str, Any]
    ) -> AnalysisResult:
        """
        Detect specific vulnerability type
        
        Args:
            code: Source code to analyze
            vulnerability_type: Type of vulnerability (sqli, xss, ssrf, etc.)
            context: Additional context
            
        Returns:
            AnalysisResult with vulnerability findings
        """
        pass
    
    @abstractmethod
    async def generate_remediation(
        self,
        vulnerability: Dict[str, Any]
    ) -> RemediationPatch:
        """
        Generate code-level remediation patch
        
        Args:
            vulnerability: Vulnerability details including code location
            
        Returns:
            RemediationPatch with suggested fix
        """
        pass
    
    @abstractmethod
    async def calculate_cvss(
        self,
        vulnerability: Dict[str, Any]
    ) -> CVSSScore:
        """
        Calculate CVSS v3 score for vulnerability
        
        Args:
            vulnerability: Vulnerability details
            
        Returns:
            CVSSScore with complete metrics
        """
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """
        Check if provider is available and responding
        
        Returns:
            True if healthy, False otherwise
        """
        pass
    
    @abstractmethod
    async def estimate_tokens(self, text: str) -> int:
        """
        Estimate token count for text
        
        Args:
            text: Input text
            
        Returns:
            Estimated token count
        """
        pass
    
    def get_provider_info(self) -> Dict[str, Any]:
        """
        Get provider information
        
        Returns:
            Dictionary with provider details
        """
        return {
            "provider": self.provider_type.value,
            "model": self.model,
            "config": {k: v for k, v in self.config.items() if k != 'api_key'}
        }


class ProviderError(Exception):
    """Base exception for provider errors"""
    pass


class ProviderUnavailableError(ProviderError):
    """Provider is unavailable or not responding"""
    pass


class ProviderQuotaExceededError(ProviderError):
    """Provider quota/rate limit exceeded"""
    pass


class ProviderAuthenticationError(ProviderError):
    """Provider authentication failed"""
    pass


class ProviderInvalidResponseError(ProviderError):
    """Provider returned invalid response"""
    pass

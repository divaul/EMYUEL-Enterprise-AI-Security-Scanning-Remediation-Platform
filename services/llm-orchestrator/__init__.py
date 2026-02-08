"""
LLM Orchestrator Service

Main service providing LLM-powered security analysis with multi-provider support
"""

from .orchestrator import LLMOrchestrator, create_orchestrator
from .providers import (
    LLMProvider,
    ProviderType,
    AnalysisType,
    AnalysisResult,
    RemediationPatch,
    CVSSScore
)

__version__ = "1.0.0"

__all__ = [
    'LLMOrchestrator',
    'create_orchestrator',
    'LLMProvider',
    'ProviderType',
    'AnalysisType',
    'AnalysisResult',
    'RemediationPatch',
    'CVSSScore'
]

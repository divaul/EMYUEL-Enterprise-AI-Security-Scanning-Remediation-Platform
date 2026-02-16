"""
LLM Orchestrator - Core orchestration logic with provider abstraction

This is the main orchestrator that manages multiple LLM providers,
handles failover, and provides a unified interface for security analysis.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from enum import Enum

from .providers.base import (
    LLMProvider,
    ProviderType,
    AnalysisType,
    AnalysisResult,
    RemediationPatch,
    CVSSScore,
    ProviderError,
    ProviderUnavailableError,
    ProviderQuotaExceededError
)
from .providers.openai_provider import OpenAIProvider
from .providers.gemini_provider import GeminiProvider
from .providers.claude_provider import ClaudeProvider


logger = logging.getLogger(__name__)


class LLMOrchestrator:
    """
    Central orchestrator for all LLM providers.
    
    Manages provider initialization, health checks, and intelligent fallback.
    Provides a unified interface for all security analysis operations.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize orchestrator with configuration
        
        Args:
            config: Configuration dictionary containing:
                - primary_provider: openai/gemini/claude
                - fallback_enabled: bool
                - providers: dict with provider configs
        """
        self.config = config
        self.primary_provider_type = ProviderType(config.get('primary_provider', 'openai'))
        self.fallback_enabled = config.get('fallback_enabled', True)
        
        # Initialize all configured providers
        self.providers: Dict[ProviderType, LLMProvider] = {}
        self._initialize_providers()
        
        # Provider health status
        self.provider_health: Dict[ProviderType, bool] = {}
        
        # Usage statistics
        self.usage_stats: Dict[str, Any] = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'fallback_count': 0,
            'provider_usage': {
                ProviderType.OPENAI.value: 0,
                ProviderType.GEMINI.value: 0,
                ProviderType.CLAUDE.value: 0
            },
            'total_tokens_used': 0
        }
        
        logger.info(f"LLM Orchestrator initialized with primary provider: {self.primary_provider_type.value}")
        logger.info(f"Configured providers: {list(self.providers.keys())}")
    
    def _initialize_providers(self):
        """Initialize all configured providers"""
        provider_configs = self.config.get('providers', {})
        
        # OpenAI
        if 'openai' in provider_configs:
            openai_config = provider_configs['openai']
            if openai_config.get('api_key'):
                try:
                    self.providers[ProviderType.OPENAI] = OpenAIProvider(
                        api_key=openai_config['api_key'],
                        model=openai_config.get('model', 'gpt-4-turbo-preview'),
                        config=openai_config
                    )
                    logger.info("OpenAI provider initialized")
                except Exception as e:
                    logger.error(f"Failed to initialize OpenAI provider: {str(e)}")
        
        # Gemini
        if 'gemini' in provider_configs:
            gemini_config = provider_configs['gemini']
            if gemini_config.get('api_key'):
                try:
                    self.providers[ProviderType.GEMINI] = GeminiProvider(
                        api_key=gemini_config['api_key'],
                        model=gemini_config.get('model', 'gemini-1.5-flash'),
                        config=gemini_config
                    )
                    logger.info("Gemini provider initialized")
                except Exception as e:
                    logger.error(f"Failed to initialize Gemini provider: {str(e)}")
        
        # Claude
        if 'claude' in provider_configs:
            claude_config = provider_configs['claude']
            if claude_config.get('api_key'):
                try:
                    self.providers[ProviderType.CLAUDE] = ClaudeProvider(
                        api_key=claude_config['api_key'],
                        model=claude_config.get('model', 'claude-3-opus-20240229'),
                        config=claude_config
                    )
                    logger.info("Claude provider initialized")
                except Exception as e:
                    logger.error(f"Failed to initialize Claude provider: {str(e)}")
        
        if not self.providers:
            raise ValueError("No LLM providers configured. Please configure at least one provider.")
    
    async def health_check_all(self) -> Dict[ProviderType, bool]:
        """
        Check health of all configured providers
        
        Returns:
            Dictionary mapping provider to health status
        """
        health_results = {}
        
        for provider_type, provider in self.providers.items():
            try:
                is_healthy = await provider.health_check()
                health_results[provider_type] = is_healthy
                self.provider_health[provider_type] = is_healthy
                logger.info(f"{provider_type.value} health check: {'healthy' if is_healthy else 'unhealthy'}")
            except Exception as e:
                health_results[provider_type] = False
                self.provider_health[provider_type] = False
                logger.error(f"{provider_type.value} health check failed: {str(e)}")
        
        return health_results
    
    def _get_fallback_order(self) -> List[ProviderType]:
        """
        Get provider fallback order based on configuration
        
        Returns:
            List of providers in priority order
        """
        # Start with primary provider
        order = [self.primary_provider_type]
        
        if not self.fallback_enabled:
            return order
        
        # Add other configured providers as fallback
        for provider_type in self.providers.keys():
            if provider_type not in order:
                order.append(provider_type)
        
        return order
    
    async def _execute_with_fallback(self, operation: str, *args, **kwargs) -> Any:
        """
        Execute operation with provider fallback logic
        
        Args:
            operation: Method name to call on provider
            *args, **kwargs: Arguments for the operation
            
        Returns:
            Result from the operation
            
        Raises:
            ProviderError: If all providers fail
        """
        fallback_order = self._get_fallback_order()
        errors = []
        
        self.usage_stats['total_requests'] += 1
        
        for i, provider_type in enumerate(fallback_order):
            if provider_type not in self.providers:
                continue
            
            provider = self.providers[provider_type]
            
            # Skip if provider is known to be unhealthy
            if self.provider_health.get(provider_type) is False:
                logger.warning(f"Skipping unhealthy provider: {provider_type.value}")
                continue
            
            try:
                logger.info(f"Attempting operation '{operation}' with provider: {provider_type.value}")
                
                # Call the operation method on the provider
                method = getattr(provider, operation)
                result = await method(*args, **kwargs)
                
                # Update statistics
                self.usage_stats['successful_requests'] += 1
                self.usage_stats['provider_usage'][provider_type.value] += 1
                
                if hasattr(result, 'tokens_used'):
                    self.usage_stats['total_tokens_used'] += result.tokens_used
                
                if i > 0:
                    self.usage_stats['fallback_count'] += 1
                    logger.info(f"Fallback successful with {provider_type.value} after {i} failures")
                
                return result
                
            except (ProviderQuotaExceededError, ProviderUnavailableError) as e:
                # These errors should trigger fallback
                logger.warning(f"Provider {provider_type.value} failed: {str(e)}")
                errors.append(f"{provider_type.value}: {str(e)}")
                self.provider_health[provider_type] = False
                continue
                
            except ProviderError as e:
                # Other provider errors might be retryable
                logger.error(f"Provider {provider_type.value} error: {str(e)}")
                errors.append(f"{provider_type.value}: {str(e)}")
                continue
        
        # All providers failed
        self.usage_stats['failed_requests'] += 1
        error_msg = "All providers failed: " + "; ".join(errors)
        logger.error(error_msg)
        raise ProviderError(error_msg)
    
    async def analyze_code(
        self,
        code: str,
        context: Dict[str, Any],
        analysis_type: AnalysisType
    ) -> AnalysisResult:
        """
        Analyze code for security issues (with fallback)
        
        Args:
            code: Source code to analyze
            context: Additional context
            analysis_type: Type of analysis
            
        Returns:
            AnalysisResult from the first available provider
        """
        return await self._execute_with_fallback(
            'analyze_code',
            code=code,
            context=context,
            analysis_type=analysis_type
        )
    
    async def trace_data_flow(
        self,
        source_code: str,
        entry_points: List[str],
        dangerous_sinks: List[str],
        context: Dict[str, Any]
    ) -> AnalysisResult:
        """
        Trace data flow from source to sink (with fallback)
        """
        return await self._execute_with_fallback(
            'trace_data_flow',
            source_code=source_code,
            entry_points=entry_points,
            dangerous_sinks=dangerous_sinks,
            context=context
        )
    
    async def detect_vulnerability(
        self,
        code: str,
        vulnerability_type: str,
        context: Dict[str, Any]
    ) -> AnalysisResult:
        """
        Detect specific vulnerability type (with fallback)
        """
        return await self._execute_with_fallback(
            'detect_vulnerability',
            code=code,
            vulnerability_type=vulnerability_type,
            context=context
        )
    
    async def generate_remediation(
        self,
        vulnerability: Dict[str, Any]
    ) -> RemediationPatch:
        """
        Generate code-level remediation (with fallback)
        """
        return await self._execute_with_fallback(
            'generate_remediation',
            vulnerability=vulnerability
        )
    
    async def calculate_cvss(
        self,
        vulnerability: Dict[str, Any]
    ) -> CVSSScore:
        """
        Calculate CVSS v3 score (with fallback)
        """
        return await self._execute_with_fallback(
            'calculate_cvss',
            vulnerability=vulnerability
        )
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get usage statistics"""
        return self.usage_stats.copy()
    
    def get_provider_status(self) -> Dict[str, Any]:
        """Get status of all providers"""
        return {
            'primary_provider': self.primary_provider_type.value,
            'fallback_enabled': self.fallback_enabled,
            'configured_providers': [p.value for p in self.providers.keys()],
            'provider_health': {p.value: h for p, h in self.provider_health.items()},
            'usage_stats': self.get_usage_stats()
        }
    
    async def close(self):
        """Cleanup resources"""
        # Close any provider connections if needed
        logger.info("LLM Orchestrator shutting down")


# Factory function for easy instantiation
def create_orchestrator(config: Dict[str, Any]) -> LLMOrchestrator:
    """
    Factory function to create LLM Orchestrator
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Initialized LLMOrchestrator instance
    """
    return LLMOrchestrator(config)

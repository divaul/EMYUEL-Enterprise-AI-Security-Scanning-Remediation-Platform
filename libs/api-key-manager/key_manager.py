"""
API Key Manager

Centralized management of API keys with error detection, recovery, and automatic failover.
Supports both CLI (interactive prompts) and GUI (dialog boxes) modes.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Callable, Any
from enum import Enum
from dataclasses import dataclass
from datetime import datetime
import json
from pathlib import Path

logger = logging.getLogger(__name__)


class KeyErrorType(Enum):
    """Types of API key errors"""
    QUOTA_EXCEEDED = "quota_exceeded"
    RATE_LIMIT = "rate_limit"
    INVALID_KEY = "invalid_key"
    EXPIRED_KEY = "expired_key"
    UNKNOWN = "unknown"


class RecoveryMode(Enum):
    """User interface mode for recovery"""
    CLI = "cli"
    GUI = "gui"
    AUTO = "auto"  # Automatic failover without user interaction


@dataclass
class APIKeyConfig:
    """API key configuration"""
    provider: str
    key: str
    is_primary: bool = True
    is_active: bool = True
    usage_count: int = 0
    last_used: Optional[datetime] = None
    last_error: Optional[str] = None


class APIKeyManager:
    """
    Manages API keys with error detection and recovery
    
    Features:
    - Multiple keys per provider (primary + backups)
    - Automatic failover
    - Interactive recovery (CLI/GUI)
    - State persistence for resume
    """
    
    def __init__(self, recovery_mode: RecoveryMode = RecoveryMode.CLI):
        """
        Initialize API key manager
        
        Args:
            recovery_mode: Mode for user interaction (CLI/GUI/AUTO)
        """
        self.recovery_mode = recovery_mode
        self.keys: Dict[str, List[APIKeyConfig]] = {}
        self.current_keys: Dict[str, int] = {}  # provider -> index in keys list
        self.error_counts: Dict[str, int] = {}
        
        # Callbacks for GUI mode
        self.on_key_error_callback: Optional[Callable] = None
        
        logger.info(f"API Key Manager initialized in {recovery_mode.value} mode")
    
    def add_key(self, provider: str, key: str, is_primary: bool = True):
        """
        Add API key for a provider
        
        Args:
            provider: Provider name (openai, gemini, claude)
            key: API key
            is_primary: Whether this is the primary key
        """
        if provider not in self.keys:
            self.keys[provider] = []
            self.current_keys[provider] = 0
        
        config = APIKeyConfig(
            provider=provider,
            key=key,
            is_primary=is_primary
        )
        
        if is_primary:
            self.keys[provider].insert(0, config)
        else:
            self.keys[provider].append(config)
        
        logger.info(f"Added {'primary' if is_primary else 'backup'} key for {provider}")
    
    def get_current_key(self, provider: str) -> Optional[str]:
        """Get current active key for provider"""
        if provider not in self.keys or not self.keys[provider]:
            return None
        
        idx = self.current_keys.get(provider, 0)
        if idx >= len(self.keys[provider]):
            return None
        
        key_config = self.keys[provider][idx]
        if key_config.is_active:
            return key_config.key
        
        return None
    
    def detect_error_type(self, error: Exception) -> KeyErrorType:
        """
        Detect type of API key error
        
        Args:
            error: Exception from LLM provider
            
        Returns:
            Type of error
        """
        error_str = str(error).lower()
        
        if any(x in error_str for x in ['quota', 'insufficient', 'limit exceeded']):
            return KeyErrorType.QUOTA_EXCEEDED
        elif any(x in error_str for x in ['rate limit', 'too many requests', '429']):
            return KeyErrorType.RATE_LIMIT
        elif any(x in error_str for x in ['invalid', 'unauthorized', '401', 'authentication']):
            return KeyErrorType.INVALID_KEY
        elif any(x in error_str for x in ['expired', 'revoked']):
            return KeyErrorType.EXPIRED_KEY
        else:
            return KeyErrorType.UNKNOWN
    
    async def execute_with_recovery(
        self,
        operation: Callable,
        provider: str,
        max_retries: int = 3
    ) -> Any:
        """
        Execute LLM operation with automatic error recovery
        
        Args:
            operation: Async function to execute
            provider: Provider name
            max_retries: Maximum retry attempts
            
        Returns:
            Result from operation
            
        Raises:
            Exception: If all recovery attempts fail
        """
        last_error = None
        
        for attempt in range(max_retries):
            try:
                # Execute operation
                result = await operation()
                
                # Success - update usage stats
                self._update_usage(provider)
                
                return result
                
            except Exception as e:
                last_error = e
                error_type = self.detect_error_type(e)
                
                logger.warning(f"API error ({error_type.value}): {str(e)}")
                
                # Try recovery
                recovered = await self._attempt_recovery(provider, error_type, attempt)
                
                if not recovered:
                    # Recovery failed
                    if attempt == max_retries - 1:
                        logger.error(f"All recovery attempts failed for {provider}")
                        raise
                    
                # Wait before retry
                if error_type == KeyErrorType.RATE_LIMIT:
                    wait_time = min(2 ** attempt, 60)  # Exponential backoff, max 60s
                    logger.info(f"Rate limited, waiting {wait_time}s...")
                    await asyncio.sleep(wait_time)
        
        raise last_error or Exception("Operation failed after retries")
    
    async def _attempt_recovery(
        self,
        provider: str,
        error_type: KeyErrorType,
        attempt: int
    ) -> bool:
        """
        Attempt to recover from API key error
        
        Returns:
            True if recovery successful, False otherwise
        """
        # Track error
        self.error_counts[provider] = self.error_counts.get(provider, 0) + 1
        
        # Mark current key as failed
        if provider in self.keys and provider in self.current_keys:
            idx = self.current_keys[provider]
            if idx < len(self.keys[provider]):
                self.keys[provider][idx].last_error = error_type.value
        
        # Try automatic failover first
        if self.recovery_mode == RecoveryMode.AUTO or attempt == 0:
            if self._try_backup_key(provider):
                logger.info(f"Automatically switched to backup key for {provider}")
                return True
        
        # Interactive recovery based on mode
        if self.recovery_mode == RecoveryMode.CLI:
            return await self._recover_cli(provider, error_type)
        elif self.recovery_mode == RecoveryMode.GUI:
            return await self._recover_gui(provider, error_type)
        
        return False
    
    def _try_backup_key(self, provider: str) -> bool:
        """Try to switch to next backup key"""
        if provider not in self.keys:
            return False
        
        current_idx = self.current_keys.get(provider, 0)
        
        # Try next keys
        for i in range(current_idx + 1, len(self.keys[provider])):
            if self.keys[provider][i].is_active:
                self.current_keys[provider] = i
                logger.info(f"Switched to backup key #{i} for {provider}")
                return True
        
        return False
    
    async def _recover_cli(self, provider: str, error_type: KeyErrorType) -> bool:
        """
        Interactive CLI recovery
        
        Shows menu and prompts user for action
        """
        print("\n" + "="*60)
        print(f"⚠️  API Key Error: {provider.upper()}")
        print("="*60)
        print(f"Error Type: {error_type.value}")
        print(f"Provider: {provider}")
        
        current_key = self.get_current_key(provider)
        if current_key:
            masked_key = current_key[:8] + "..." + current_key[-4:]
            print(f"Current Key: {masked_key}")
        
        print("\nOptions:")
        print("  1) Enter new API key")
        print("  2) Use backup key (if available)")
        print("  3) Switch to different provider")
        print("  4) Retry with current key")
        print("  5) Abort scan")
        
        while True:
            try:
                choice = input("\nYour choice [1-5]: ").strip()
                
                if choice == "1":
                    new_key = input(f"Enter new {provider} API key: ").strip()
                    if new_key:
                        self.add_key(provider, new_key, is_primary=True)
                        self.current_keys[provider] = 0
                        print("✓ API key updated")
                        return True
                
                elif choice == "2":
                    if self._try_backup_key(provider):
                        print("✓ Switched to backup key")
                        return True
                    else:
                        print("✗ No backup keys available")
                        continue
                
                elif choice == "3":
                    print("\nAvailable providers:")
                    providers = ["openai", "gemini", "claude"]
                    for i, p in enumerate(providers, 1):
                        if p != provider:
                            print(f"  {i}) {p}")
                    
                    # This would need to be handled by scanner
                    print("Note: Provider switching must be configured in scanner")
                    return False
                
                elif choice == "4":
                    print("Retrying with current key...")
                    return True
                
                elif choice == "5":
                    print("Scan aborted by user")
                    raise KeyboardInterrupt("User aborted scan")
                
                else:
                    print("Invalid choice, please try again")
                    
            except (EOFError, KeyboardInterrupt):
                print("\nScan interrupted")
                raise
    
    async def _recover_gui(self, provider: str, error_type: KeyErrorType) -> bool:
        """
        GUI recovery via callback
        
        Calls registered callback to show dialog
        """
        if self.on_key_error_callback:
            return await self.on_key_error_callback(provider, error_type)
        else:
            logger.error("GUI callback not registered, falling back to auto mode")
            return self._try_backup_key(provider)
    
    def _update_usage(self, provider: str):
        """Update usage statistics for current key"""
        if provider in self.keys and provider in self.current_keys:
            idx = self.current_keys[provider]
            if idx < len(self.keys[provider]):
                self.keys[provider][idx].usage_count += 1
                self.keys[provider][idx].last_used = datetime.utcnow()
    
    def set_gui_callback(self, callback: Callable):
        """Set callback for GUI error handling"""
        self.on_key_error_callback = callback
    
    def get_stats(self) -> Dict[str, Any]:
        """Get usage statistics"""
        stats = {}
        
        for provider, keys in self.keys.items():
            stats[provider] = {
                'total_keys': len(keys),
                'active_keys': sum(1 for k in keys if k.is_active),
                'current_index': self.current_keys.get(provider, 0),
                'error_count': self.error_counts.get(provider, 0),
                'keys': [
                    {
                        'is_primary': k.is_primary,
                        'is_active': k.is_active,
                        'usage_count': k.usage_count,
                        'last_used': k.last_used.isoformat() if k.last_used else None,
                        'last_error': k.last_error
                    }
                    for k in keys
                ]
            }
        
        return stats
    
    def save_state(self, filepath: Path):
        """Save key manager state to file"""
        state = {
            'current_keys': self.current_keys,
            'error_counts': self.error_counts,
            'stats': self.get_stats()
        }
        
        with open(filepath, 'w') as f:
            json.dump(state, f, indent=2)
    
    def load_state(self, filepath: Path):
        """Load key manager state from file"""
        if not filepath.exists():
            return
        
        with open(filepath) as f:
            state = json.load(f)
        
        self.current_keys = state.get('current_keys', {})
        self.error_counts = state.get('error_counts', {})

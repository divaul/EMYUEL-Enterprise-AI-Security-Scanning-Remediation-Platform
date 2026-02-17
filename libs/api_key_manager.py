"""
API Key Manager - Error handling and recovery for LLM API keys
"""

# Import from actual implementation in api-key-manager directory
import sys
from pathlib import Path

# Add api-key-manager to path
current_dir = Path(__file__).parent
api_key_dir = current_dir / "api-key-manager"
if api_key_dir.exists():
    sys.path.insert(0, str(api_key_dir))

try:
    from api_key_manager import APIKeyManager, RecoveryMode, ProviderConfig, KeyStatus
    __all__ = ['APIKeyManager', 'RecoveryMode', 'ProviderConfig', 'KeyStatus']
except ImportError:
    # Fallback: create minimal implementation
    from enum import Enum
    
    class RecoveryMode(Enum):
        """Recovery mode for API key errors"""
        CLI = "cli"
        GUI = "gui"
        AUTOMATIC = "automatic"
    
    class APIKeyManager:
        """Minimal API Key Manager stub"""
        def __init__(self, recovery_mode=RecoveryMode.CLI):
            self.recovery_mode = recovery_mode
            self.keys = {}
        
        def add_key(self, provider, key, is_primary=True):
            """Add API key for provider"""
            if provider not in self.keys:
                self.keys[provider] = []
            self.keys[provider].append({
                'key': key,
                'is_primary': is_primary
            })
        
        def get_key(self, provider):
            """Get API key for provider"""
            if provider in self.keys and self.keys[provider]:
                return self.keys[provider][0]['key']
            return None
        
        def save_keys(self):
            """Save keys (stub implementation)"""
            pass
        
        async def handle_error(self, provider, error_message):
            """Handle API key error"""
            print(f"API Key Error for {provider}: {error_message}")
            return None
    
    class ProviderConfig:
        pass
    
    class KeyStatus:
        pass
    
    __all__ = ['APIKeyManager', 'RecoveryMode', 'ProviderConfig', 'KeyStatus']

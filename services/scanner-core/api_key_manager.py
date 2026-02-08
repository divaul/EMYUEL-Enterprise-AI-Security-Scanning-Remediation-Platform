"""
API Key Manager Helper - Simplified version for scanner

Manages API keys for LLM providers
"""

from pathlib import Path
import json
from typing import Optional, Dict, Any


class APIKeyManager:
    """Manage API keys for LLM providers"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize API key manager
        
        Args:
            config_path: Path to API key config file
        """
        if config_path is None:
            config_path = Path.home() / ".emyuel" / "api_keys.json"
        
        self.config_path = Path(config_path)
        self.keys = self._load_keys()
    
    def _load_keys(self) -> Dict[str, Any]:
        """Load API keys from config file"""
        if not self.config_path.exists():
            return {}
        
        try:
            with open(self.config_path, 'r') as f:
                data = json.load(f)
                return data
        except Exception as e:
            print(f"[API Keys] Error loading keys: {e}")
            return {}
    
    def get_key(self, provider: str) -> Optional[str]:
        """
        Get API key for provider
        
        Args:
            provider: Provider name (openai, gemini, claude)
            
        Returns:
            API key or None
        """
        provider_keys = self.keys.get(provider, [])
        
        if not provider_keys:
            return None
        
        # Return first non-backup key
        for key_info in provider_keys:
            if not key_info.get('is_backup', False):
                return key_info.get('key')
        
        # If no non-backup key, return first key
        return provider_keys[0].get('key') if provider_keys else None
    
    def set_key(self, provider: str, key: str):
        """
        Set API key for provider
        
        Args:
            provider: Provider name
            key: API key
        """
        if provider not in self.keys:
            self.keys[provider] = []
        
        # Add key
        self.keys[provider].append({
            'key': key,
            'is_backup': False
        })
        
        self._save_keys()
    
    def _save_keys(self):
        """Save keys to config file"""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(self.config_path, 'w') as f:
            json.dump(self.keys, f, indent=2)

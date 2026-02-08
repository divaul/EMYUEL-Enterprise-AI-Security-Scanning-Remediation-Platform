"""
Brute Force Detector - Advanced Authentication Testing

Supports:
- Default credentials testing
- Wordlist-based attacks
- Exhaustive character-based brute force
- Multiple character sets (lowercase, uppercase, numbers, symbols)
"""

import asyncio
import aiohttp
import itertools
import string
from typing import Dict, List, Optional, Tuple, Set
from datetime import datetime
import json
from pathlib import Path


class BruteForceDetector:
    """Advanced brute force authentication testing"""
    
    # Character sets
    CHARSETS = {
        'lowercase': string.ascii_lowercase,
        'uppercase': string.ascii_uppercase,
        'numbers': string.digits,
        'symbols': '!@#$%^&*()-_=+[]{}|;:\',.<>?/~`',
        'all': string.ascii_lowercase + string.ascii_uppercase + string.digits + '!@#$%^&*()-_=+[]{}|;:\',.<>?/~`'
    }
    
    def __init__(self, 
                 strategy='hybrid',
                 charsets=None,
                 min_length=1,
                 max_length=4,
                 rate_limit=0.1,
                 max_attempts=10000,
                 stop_on_success=True):
        """
        Initialize brute force detector
        
        Args:
            strategy: 'default', 'wordlist', 'exhaustive', 'hybrid'
            charsets: List of charset names or 'all'
            min_length: Minimum password length for exhaustive
            max_length: Maximum password length for exhaustive (WARNING: >6 is SLOW)
            rate_limit: Delay between attempts (seconds)
            max_attempts: Maximum total attempts (safety limit)
            stop_on_success: Stop after first valid credential found
        """
        self.strategy = strategy
        self.charsets = charsets or ['lowercase', 'numbers']
        self.min_length = min_length
        self.max_length = max_length
        self.rate_limit = rate_limit
        self.max_attempts = max_attempts
        self.stop_on_success = stop_on_success
        
        # Statistics
        self.attempts = 0
        self.start_time = None
        self.found_credentials = []
        
        # Load wordlists
        self.default_credentials = self._load_default_credentials()
        self.common_passwords = self._load_common_passwords()
        self.common_usernames = self._load_common_usernames()
    
    def _load_default_credentials(self) -> Dict[str, List[str]]:
        """Load common default credentials"""
        # Built-in defaults
        return {
            'admin': ['admin', 'password', 'admin123', '1234', 'root'],
            'root': ['root', 'toor', 'password', '123456'],
            'administrator': ['administrator', 'admin', 'password'],
            'user': ['user', 'password', 'user123'],
            'test': ['test', 'password', 'test123'],
            'guest': ['guest', 'password', ''],
            'demo': ['demo', 'password', 'demo123']
        }
    
    def _load_common_passwords(self) -> List[str]:
        """Load top common passwords"""
        return [
            '123456', 'password', '12345678', 'qwerty', '123456789',
            '12345', '1234', '111111', '1234567', 'dragon',
            '123123', 'baseball', 'iloveyou', 'trustno1', '1234567890',
            'sunshine', 'master', '123321', 'letmein', 'abc123',
            'monkey', '1qaz2wsx', 'admin', 'welcome', 'login',
            'admin123', 'password1', 'qwertyuiop', 'solo', 'passw0rd',
            'starwars', 'qazwsx', 'freedom', 'whatever', 'Password',
            '000000', 'ninja', 'azerty', 'Football', '121212',
            'bailey', 'princess', 'flower', 'zxcvbnm', 'shadow',
            'michael', 'jordan', 'hunter', 'tigger', 'computer'
        ]
    
    def _load_common_usernames(self) -> List[str]:
        """Load common usernames"""
        return [
            'admin', 'administrator', 'root', 'user', 'test',
            'guest', 'demo', 'support', 'manager', 'webmaster',
            'postmaster', 'info', 'sales', 'backup', 'operator'
        ]
    
    def _get_charset(self) -> str:
        """Get combined character set based on configuration"""
        if self.charsets == ['all'] or 'all' in self.charsets:
            return self.CHARSETS['all']
        
        combined = ''
        for cs_name in self.charsets:
            if cs_name in self.CHARSETS:
                combined += self.CHARSETS[cs_name]
        
        # Remove duplicates while preserving order
        return ''.join(dict.fromkeys(combined))
    
    def generate_exhaustive_passwords(self, length: int) -> itertools.product:
        """
        Generate all possible password combinations for given length
        
        WARNING: This can generate MASSIVE number of combinations!
        - 4 chars with lowercase only (26^4) = 456,976
        - 4 chars with all chars (95^4) = 81,450,625
        - 8 chars with all chars (95^8) = 6.6 quadrillion!
        """
        charset = self._get_charset()
        return itertools.product(charset, repeat=length)
    
    async def detect(self, target_url: str, username: Optional[str] = None) -> Dict:
        """
        Main detection method - orchestrates brute force attack
        
        Returns dict with:
            - found_credentials: List of (username, password) tuples
            - attempts: Total attempts made
            - time_taken: Seconds elapsed
            - strategy_used: Which strategy succeeded
        """
        self.start_time = datetime.now()
        self.attempts = 0
        self.found_credentials = []
        
        print(f"[BRUTE FORCE] Starting attack on: {target_url}")
        print(f"[BRUTE FORCE] Strategy: {self.strategy}")
        print(f"[BRUTE FORCE] Character sets: {self.charsets}")
        print(f"[BRUTE FORCE] Length range: {self.min_length}-{self.max_length}")
        
        # Strategy 1: Default Credentials (fastest)
        if self.strategy in ['default', 'hybrid']:
            print("[BRUTE FORCE] Trying default credentials...")
            found = await self._try_default_credentials(target_url, username)
            if found and self.stop_on_success:
                return self._build_result('default')
        
        # Strategy 2: Wordlist Attack
        if self.strategy in ['wordlist', 'hybrid']:
            print("[BRUTE FORCE] Trying wordlist attack...")
            found = await self._try_wordlist(target_url, username)
            if found and self.stop_on_success:
                return self._build_result('wordlist')
        
        # Strategy 3: Exhaustive Brute Force (slowest)
        if self.strategy in ['exhaustive', 'hybrid']:
            print("[BRUTE FORCE] Starting exhaustive brute force...")
            print(f"[WARNING] This may take a VERY long time!")
            found = await self._try_exhaustive(target_url, username)
            if found:
                return self._build_result('exhaustive')
        
        return self._build_result('none')
    
    async def _try_default_credentials(self, target_url: str, username: Optional[str]) -> bool:
        """Try common default username/password combinations"""
        if username:
            # Try specific username with its defaults
            if username in self.default_credentials:
                for password in self.default_credentials[username]:
                    if await self._test_credential(target_url, username, password):
                        return True
        else:
            # Try all default combinations
            for user, passwords in self.default_credentials.items():
                for password in passwords:
                    if await self._test_credential(target_url, user, password):
                        return True
        
        return False
    
    async def _try_wordlist(self, target_url: str, username: Optional[str]) -> bool:
        """Try wordlist-based attack"""
        usernames = [username] if username else self.common_usernames
        
        for user in usernames:
            for password in self.common_passwords:
                if await self._test_credential(target_url, user, password):
                    return True
        
        return False
    
    async def _try_exhaustive(self, target_url: str, username: Optional[str]) -> bool:
        """Try exhaustive character-based brute force"""
        charset = self._get_charset()
        total_combinations = sum(len(charset) ** length 
                                for length in range(self.min_length, self.max_length + 1))
        
        print(f"[BRUTE FORCE] Charset: {charset[:20]}... ({len(charset)} chars)")
        print(f"[BRUTE FORCE] Estimated combinations: {total_combinations:,}")
        
        if total_combinations > 1000000:
            print(f"[WARNING] {total_combinations:,} combinations will take VERY long!")
            print(f"[TIP] Consider reducing max_length or using fewer character sets")
        
        usernames = [username] if username else self.common_usernames
        
        # Try each length incrementally
        for length in range(self.min_length, self.max_length + 1):
            print(f"[BRUTE FORCE] Trying length {length}...")
            
            for password_tuple in self.generate_exhaustive_passwords(length):
                password = ''.join(password_tuple)
                
                for user in usernames:
                    if await self._test_credential(target_url, user, password):
                        return True
                
                # Safety check
                if self.attempts >= self.max_attempts:
                    print(f"[BRUTE FORCE] Max attempts ({self.max_attempts}) reached!")
                    return False
        
        return False
    
    async def _test_credential(self, target_url: str, username: str, password: str) -> bool:
        """
        Test a single username/password combination
        
        Returns True if credential is valid
        """
        self.attempts += 1
        
        # Progress feedback every 100 attempts
        if self.attempts % 100 == 0:
            elapsed = (datetime.now() - self.start_time).total_seconds()
            rate = self.attempts / elapsed if elapsed > 0 else 0
            print(f"[PROGRESS] Attempts: {self.attempts} | Rate: {rate:.1f}/sec | Testing: {username}:{password[:3]}...")
        
        # Rate limiting
        if self.rate_limit > 0:
            await asyncio.sleep(self.rate_limit)
        
        # TODO: Implement actual HTTP testing
        # For now, simulate testing
        # In real implementation, this would make HTTP request and check response
        
        # Placeholder: randomly succeed (replace with real HTTP check)
        # Real implementation would do:
        # async with aiohttp.ClientSession() as session:
        #     auth = aiohttp.BasicAuth(username, password)
        #     async with session.get(target_url, auth=auth) as resp:
        #         if resp.status == 200:  # Success!
        #             self.found_credentials.append((username, password))
        #             print(f"[SUCCESS] Found valid credential: {username}:{password}")
        #             return True
        
        return False  # Placeholder
    
    def _build_result(self, strategy_used: str) -> Dict:
        """Build final result dictionary"""
        elapsed = (datetime.now() - self.start_time).total_seconds()
        
        return {
            'found_credentials': self.found_credentials,
            'attempts': self.attempts,
            'time_taken': elapsed,
            'strategy_used': strategy_used,
            'success': len(self.found_credentials) > 0
        }


# Example usage
if __name__ == '__main__':
    # Example 1: Wordlist attack
    detector1 = BruteForceDetector(strategy='wordlist')
    
    # Example 2: Exhaustive with lowercase + numbers (fast)
    detector2 = BruteForceDetector(
        strategy='exhaustive',
        charsets=['lowercase', 'numbers'],
        min_length=1,
        max_length=4,
        rate_limit=0.01
    )
    
    # Example 3: Full exhaustive with ALL characters (SLOW!)
    detector3 = BruteForceDetector(
        strategy='exhaustive',
        charsets=['all'],
        min_length=1,
        max_length=3,  # Only 3! 95^3 = 857,375 combos
        rate_limit=0.001,
        max_attempts=100000
    )
    
    print("Brute Force Detector initialized")
    print(f"Example 2 charset: {detector2._get_charset()}")
    print(f"Example 3 charset: {detector3._get_charset()[:50]}...")

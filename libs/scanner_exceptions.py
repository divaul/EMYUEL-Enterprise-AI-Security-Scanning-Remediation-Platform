"""
Custom Exceptions for EMYUEL Scanner

Provides specialized exceptions for different error scenarios
"""


class APIError(Exception):
    """API-related error that should trigger scan pause"""
    
    def __init__(self, code: str, message: str):
        """
        Initialize API error
        
        Args:
            code: Error code (API_KEY_INVALID, API_TIMEOUT, API_QUOTA_EXCEEDED)
            message: Human-readable error message
        """
        self.code = code
        self.message = message
        super().__init__(f"{code}: {message}")


class ScanPausedException(Exception):
    """
    Scan paused - not a real error, just a control flow signal
    
    This exception is used to pause a scan and save its state
    for later resumption
    """
    
    def __init__(self, reason: str, state: dict):
        """
        Initialize scan pause exception
        
        Args:
            reason: Human-readable reason for pause
            state: Dictionary containing scan state for resume
        """
        self.reason = reason
        self.state = state
        super().__init__(reason)

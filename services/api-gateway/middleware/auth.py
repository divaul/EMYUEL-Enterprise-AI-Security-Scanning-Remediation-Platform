"""
Authentication Middleware

JWT token validation middleware
"""

from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
import logging

logger = logging.getLogger(__name__)


class AuthenticationMiddleware(BaseHTTPMiddleware):
    """JWT authentication middleware"""
    
    def __init__(self, app):
        super().__init__(app)
        # Paths that don't require authentication
        self.exclude_paths = [
            "/health",
            "/api/v1/auth/login",
            "/api/v1/auth/register",
            "/api/docs",
            "/api/redoc",
            "/openapi.json"
        ]
    
    async def dispatch(self, request: Request, call_next):
        """Process request with authentication check"""
        
        # Skip authentication for excluded paths
        if any(request.url.path.startswith(path) for path in self.exclude_paths):
            return await call_next(request)
        
        # Get authorization header
        auth_header = request.headers.get("Authorization")
        
        if not auth_header:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing authorization header",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        # Validate Bearer token format
        try:
            scheme, token = auth_header.split()
            if scheme.lower() != "bearer":
                raise ValueError()
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authorization header format",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        # TODO: Validate JWT token
        # 1. Decode JWT
        # 2. Verify signature
        # 3. Check expiration
        # 4. Load user from database
        # 5. Attach user to request.state
        
        # For now, just pass through
        # request.state.user = decoded_user
        
        return await call_next(request)

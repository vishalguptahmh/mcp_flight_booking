"""
JWT Token Validator for OAuth 2.1
Handles token validation and verification logic
"""

import jwt
import time
from typing import Dict, Optional
from fastapi import HTTPException, status, Header

from ..config.auth_config import OAUTH_CONFIG


class TokenValidator:
    """JWT token validation and verification"""
    
    def __init__(self, config=None):
        self.config = config or OAUTH_CONFIG
        self.secret_key = self.config["jwt_secret"]
        self.algorithm = self.config["algorithm"]
        self.expected_audience = self.config["expected_audience"]
        self.expected_issuer = self.config["expected_issuer"]
    
    def verify_token(self, token: str) -> Dict:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm],
                audience=self.expected_audience,
                issuer=self.expected_issuer
            )
            
            # Additional expiry check
            if payload.get("exp", 0) < time.time():
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token expired"
                )
            
            return payload
            
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired",
                headers={"WWW-Authenticate": "Bearer"}
            )
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"}
            )
    
    def extract_token_from_header(self, auth_header: str) -> str:
        """Extract token from Authorization header"""
        if not auth_header:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing authorization header",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        if not auth_header.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authorization header format",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        return auth_header[7:]  # Remove "Bearer " prefix
    
    def validate_scopes(self, token_payload: Dict, required_scopes: list) -> bool:
        """Validate token has required scopes"""
        token_scopes = token_payload.get("scope", "").split()
        return all(scope in token_scopes for scope in required_scopes)


# Global validator instance
token_validator = TokenValidator()


def verify_oauth_token(authorization: str = Header(None)) -> Dict:
    """FastAPI dependency for OAuth token verification"""
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header required",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    token = token_validator.extract_token_from_header(authorization)
    return token_validator.verify_token(token)

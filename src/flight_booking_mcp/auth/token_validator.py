"""
JWT Token Validator for OAuth 2.1
Handles token validation and verification logic
"""

import jwt
import time
import logging
from typing import Dict, Optional
from datetime import datetime
from fastapi import HTTPException, status, Header

from ..config.auth_config import get_oauth_config

# Configure logging for token validation
import os
log_dir = os.path.dirname(os.path.abspath(__file__))
log_file = os.path.join(log_dir, 'token_validation.log')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - [%(levelname)s] - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("VG_Token_Validator")


class TokenValidator:
    """JWT token validation and verification"""
    
    def __init__(self, config=None):
        self.config = config or get_oauth_config()
        self.secret_key = self.config["jwt_secret"]
        self.algorithm = self.config["algorithm"]
        self.expected_audience = self.config["expected_audience"]
        self.expected_issuer = self.config["expected_issuer"]
    
    def verify_token(self, token: str) -> Dict:
        """Verify and decode JWT token"""
        logger.info("🔍 Starting token validation process")
        logger.info(f"   🏷️  System: VG_FLIGHTMCP_2024")
        logger.info(f"   ⏰ Timestamp: {datetime.now().isoformat()}")
        
        try:
            # Log token structure (full token for debugging)
            logger.info(f"   🎫 Full Token: {token}")
            logger.info(f"   🔧 Algorithm: {self.algorithm}")
            logger.info(f"   👥 Expected audience: {self.expected_audience}")
            logger.info(f"   🏢 Expected issuer: {self.expected_issuer}")
            
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm],
                audience=self.expected_audience,
                issuer=self.expected_issuer
            )
            
            # Log successful validation
            logger.info("✅ Token signature validation: SUCCESS")
            logger.info(f"   📋 Full Payload: {payload}")
            logger.info(f"   👤 Subject: {payload.get('sub', 'N/A')}")
            logger.info(f"   🎯 Audience: {payload.get('aud', 'N/A')}")
            logger.info(f"   ⏳ Expires: {payload.get('exp', 'N/A')}")
            logger.info(f"   🏷️  System: VG_FLIGHTMCP_2024")
            
            # Additional expiry check
            if payload.get("exp", 0) < time.time():
                logger.error("❌ Token validation failed: EXPIRED")
                logger.error(f"   ⏰ Token exp: {payload.get('exp', 0)}")
                logger.error(f"   ⏰ Current time: {time.time()}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token expired"
                )
            
            logger.info("✅ Token validation: COMPLETE SUCCESS")
            logger.info("-" * 60)
            return payload
            
        except jwt.ExpiredSignatureError as e:
            logger.error("❌ Token validation failed: EXPIRED SIGNATURE")
            logger.error(f"   🚨 Error: {str(e)}")
            logger.error("-" * 60)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired",
                headers={"WWW-Authenticate": "Bearer"}
            )
        except jwt.InvalidTokenError as e:
            logger.error("❌ Token validation failed: INVALID TOKEN")
            logger.error(f"   🚨 Error: {str(e)}")
            logger.error(f"   🎫 Token preview: {token[:20] if token else 'None'}...")
            logger.error("-" * 60)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"}
            )
    
    def extract_token_from_header(self, auth_header: str) -> str:
        """Extract token from Authorization header"""
        logger.info("🔗 Extracting token from Authorization header")
        logger.info(f"   🏷️  System: VG_FLIGHTMCP_2024")
        
        if not auth_header:
            logger.error("❌ Authorization header extraction failed: MISSING HEADER")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing authorization header",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        logger.info(f"   📋 Header present: {len(auth_header)} characters")
        logger.info(f"   🔍 Header preview: {auth_header[:20]}...")
        
        if not auth_header.startswith("Bearer "):
            logger.error("❌ Authorization header extraction failed: INVALID FORMAT")
            logger.error(f"   📋 Header preview: {auth_header[:20]}...")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authorization header format",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        token = auth_header[7:]  # Remove "Bearer " prefix
        logger.info("✅ Token extraction: SUCCESS")
        logger.info(f"   🎫 Full Token: {token}")
        logger.info(f"   🎫 Token length: {len(token)} characters")
        logger.info(f"   �️  System: VG_FLIGHTMCP_2024")
        
        return token
    
    def validate_scopes(self, token_payload: Dict, required_scopes: list) -> bool:
        """Validate token has required scopes"""
        token_scopes = token_payload.get("scope", "").split()
        return all(scope in token_scopes for scope in required_scopes)


# Global validator instance - lazy loaded
_token_validator = None

def get_token_validator():
    """Get global token validator instance with lazy initialization"""
    global _token_validator
    if _token_validator is None:
        _token_validator = TokenValidator()
    return _token_validator


def verify_oauth_token(authorization: str = Header(None)) -> Dict:
    """FastAPI dependency for OAuth token verification"""
    logger.info("🔐 OAuth token verification requested")
    logger.info(f"   🏷️  System: VG_FLIGHTMCP_2024")
    logger.info(f"   ⏰ Timestamp: {datetime.now().isoformat()}")
    
    if not authorization:
        logger.error("❌ OAuth verification failed: NO AUTHORIZATION HEADER")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header required",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    logger.info("🔗 Processing authorization header")
    token_validator = get_token_validator()
    token = token_validator.extract_token_from_header(authorization)
    
    logger.info("🔍 Proceeding with token validation")
    result = token_validator.verify_token(token)
    
    logger.info("✅ OAuth verification: COMPLETE SUCCESS")
    logger.info("=" * 60)
    
    return result

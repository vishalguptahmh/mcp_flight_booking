"""
OAuth 2.1 Authorization Server
Clean implementation following Single Responsibility Principle
"""

from fastapi import FastAPI, HTTPException, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import jwt
import secrets
import time
from datetime import datetime, timedelta
from typing import Optional, Dict
import uvicorn
import base64
import hashlib

from ..config.auth_config import AUTH_SERVER_CONFIG, OAUTH_CLIENT_CONFIG


class OAuthServer:
    """OAuth 2.1 Authorization Server implementation"""
    
    def __init__(self, config=None):
        self.config = config or AUTH_SERVER_CONFIG
        self.secret_key = self.config["secret_key"]
        self.algorithm = self.config["algorithm"]
        self.issuer = self.config["issuer"]
        self.audience = self.config["audience"]
        
        # In-memory storage (use database in production)
        self.authorization_codes = {}
        self.access_tokens = {}
        self.clients = {
            "mcp-client": {
                "client_secret": "mcp-client-secret",
                "redirect_uris": ["http://localhost:3000/callback", "urn:ietf:wg:oauth:2.0:oob"],
                "grant_types": ["authorization_code", "refresh_token"],
                "response_types": ["code"],
                "scopes": ["read", "write"]
            }
        }
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(hours=1)
        
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "iss": self.issuer,
            "aud": self.audience
        })
        
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def verify_client(self, client_id: str, client_secret: str = None) -> bool:
        """Verify client credentials"""
        if client_id not in self.clients:
            return False
        
        if client_secret and self.clients[client_id]["client_secret"] != client_secret:
            return False
            
        return True
    
    def generate_authorization_code(self, client_id: str, redirect_uri: str, scope: str, 
                                  code_challenge: str = None, code_challenge_method: str = None) -> str:
        """Generate authorization code for OAuth flow"""
        code = secrets.token_urlsafe(32)
        self.authorization_codes[code] = {
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "scope": scope,
            "code_challenge": code_challenge,
            "code_challenge_method": code_challenge_method,
            "expires_at": time.time() + 600,  # 10 minutes
            "used": False
        }
        return code
    
    def exchange_code_for_token(self, code: str, client_id: str, client_secret: str,
                               redirect_uri: str, code_verifier: str = None) -> dict:
        """Exchange authorization code for access token"""
        if code not in self.authorization_codes:
            raise HTTPException(status_code=400, detail="Invalid authorization code")
        
        code_data = self.authorization_codes[code]
        
        # Validate code
        if code_data["used"] or time.time() > code_data["expires_at"]:
            raise HTTPException(status_code=400, detail="Authorization code expired or used")
        
        if code_data["client_id"] != client_id or code_data["redirect_uri"] != redirect_uri:
            raise HTTPException(status_code=400, detail="Invalid client or redirect URI")
        
        # Verify PKCE if present
        if code_data["code_challenge"]:
            if not code_verifier:
                raise HTTPException(status_code=400, detail="Code verifier required")
            
            if code_data["code_challenge_method"] == "S256":
                expected_challenge = base64.urlsafe_b64encode(
                    hashlib.sha256(code_verifier.encode()).digest()
                ).decode().rstrip("=")
            else:
                expected_challenge = code_verifier
            
            if expected_challenge != code_data["code_challenge"]:
                raise HTTPException(status_code=400, detail="Invalid code verifier")
        
        # Mark code as used
        code_data["used"] = True
        
        # Create access token
        token_data = {
            "sub": "demo-user",
            "client_id": client_id,
            "scope": code_data["scope"],
            "resource": "http://localhost:8000"
        }
        
        access_token = self.create_access_token(token_data)
        
        return {
            "access_token": access_token,
            "token_type": "Bearer",
            "expires_in": 3600,
            "scope": code_data["scope"]
        }


def create_oauth_app(oauth_server: OAuthServer) -> FastAPI:
    """Create FastAPI app with OAuth endpoints"""
    app = FastAPI(
        title="OAuth 2.1 Authorization Server",
        description="RFC-compliant OAuth 2.1 server for MCP",
        version="1.0.0"
    )
    
    @app.get("/.well-known/oauth-authorization-server")
    async def authorization_server_metadata():
        """OAuth 2.0 Authorization Server Metadata (RFC 8414)"""
        base_url = f"http://{oauth_server.config['host']}:{oauth_server.config['port']}"
        return {
            "issuer": oauth_server.issuer,
            "authorization_endpoint": f"{base_url}/oauth/authorize",
            "token_endpoint": f"{base_url}/oauth/token",
            "jwks_uri": f"{base_url}/.well-known/jwks.json",
            "registration_endpoint": f"{base_url}/oauth/register",
            "introspection_endpoint": f"{base_url}/oauth/introspect",
            "response_types_supported": ["code"],
            "grant_types_supported": ["authorization_code", "refresh_token"],
            "code_challenge_methods_supported": ["S256", "plain"],
            "scopes_supported": ["read", "write"],
            "token_endpoint_auth_methods_supported": ["client_secret_basic", "client_secret_post"],
            "subject_types_supported": ["public"]
        }
    
    @app.get("/.well-known/jwks.json")
    async def jwks():
        """JSON Web Key Set for token verification"""
        return {
            "keys": [
                {
                    "kty": "oct",
                    "use": "sig",
                    "alg": "HS256",
                    "k": base64.urlsafe_b64encode(oauth_server.secret_key.encode()).decode().rstrip("="),
                    "kid": "1"
                }
            ]
        }
    
    @app.get("/oauth/authorize")
    async def authorize(
        response_type: str,
        client_id: str,
        redirect_uri: str,
        scope: str = "read",
        code_challenge: Optional[str] = None,
        code_challenge_method: Optional[str] = None,
        resource: Optional[str] = None
    ):
        """Authorization endpoint"""
        if not oauth_server.verify_client(client_id):
            raise HTTPException(status_code=400, detail="Invalid client")
        
        # Generate authorization code
        auth_code = oauth_server.generate_authorization_code(
            client_id, redirect_uri, scope, code_challenge, code_challenge_method
        )
        
        if redirect_uri == "urn:ietf:wg:oauth:2.0:oob":
            # Out-of-band flow
            return HTMLResponse(f"""
            <html><body>
                <h2>Authorization Code</h2>
                <p>Copy this code: <strong>{auth_code}</strong></p>
                <p>Use this code in your application to get an access token.</p>
            </body></html>
            """)
        else:
            # Standard redirect
            return RedirectResponse(f"{redirect_uri}?code={auth_code}")
    
    @app.post("/oauth/token")
    async def token(
        grant_type: str = Form(...),
        code: str = Form(...),
        redirect_uri: str = Form(...),
        client_id: str = Form(...),
        client_secret: str = Form(...),
        code_verifier: Optional[str] = Form(None),
        resource: Optional[str] = Form(None)
    ):
        """Token endpoint"""
        if grant_type != "authorization_code":
            raise HTTPException(status_code=400, detail="Unsupported grant type")
        
        if not oauth_server.verify_client(client_id, client_secret):
            raise HTTPException(status_code=400, detail="Invalid client credentials")
        
        return oauth_server.exchange_code_for_token(
            code, client_id, client_secret, redirect_uri, code_verifier
        )
    
    @app.post("/oauth/introspect")
    async def introspect(token: str = Form(...)):
        """Token introspection endpoint (RFC 7662)"""
        try:
            payload = jwt.decode(
                token, oauth_server.secret_key, 
                algorithms=[oauth_server.algorithm]
            )
            return {
                "active": True,
                "client_id": payload.get("client_id"),
                "scope": payload.get("scope"),
                "sub": payload.get("sub"),
                "exp": payload.get("exp"),
                "iat": payload.get("iat")
            }
        except jwt.InvalidTokenError:
            return {"active": False}
    
    return app


def main():
    # Create OAuth server instance
    oauth_server = OAuthServer()
    
    # Create FastAPI app
    app = create_oauth_app(oauth_server)
    
    print("🔐 Starting Mock OAuth Authorization Server")
    print(f" on http://{oauth_server.config['host']}:{oauth_server.config['port']}")
    print(f"📋 Authorization Server Metadata: http://{oauth_server.config['host']}:{oauth_server.config['port']}/.well-known/oauth-authorization-server")
    print(f"🔑 JWKS: http://{oauth_server.config['host']}:{oauth_server.config['port']}/.well-known/jwks.json")
    
    uvicorn.run(
        app,
        host=oauth_server.config["host"],
        port=oauth_server.config["port"],
        log_level="info"
    )

if __name__ == "__main__":
    main()

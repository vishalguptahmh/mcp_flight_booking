"""
OAuth 2.1 Authorization Server
Author: Vishal Gupta
System: VG_FLIGHTMCP_2024
"""

from fastapi import FastAPI, HTTPException, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
import jwt
import secrets
import time
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict
import uvicorn
import base64
import hashlib
import urllib.parse

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

from ..config.auth_config import get_auth_server_config, get_valid_clients_cached, get_callback_urls, get_auth_server_url

# Configure logging
import os
log_dir = os.path.dirname(os.path.abspath(__file__))
log_file = os.path.join(log_dir, 'oauth_server.log')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - [%(levelname)s] - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("VG_OAuth_Server")

# Add request tracking
def log_request(request: Request, endpoint: str, details: str = ""):
    """Log OAuth requests"""
    client_ip = request.client.host if request.client else "unknown"
    logger.info(f"OAuth Request: {endpoint} from {client_ip} - {details}")


class OAuthServer:
    """OAuth 2.1 Authorization Server implementation"""
    
    def __init__(self, config=None):
        self.config = config or get_auth_server_config()
        self.secret_key = self.config["secret_key"]
        self.algorithm = self.config["algorithm"]
        self.issuer = self.config["issuer"]
        self.audience = self.config["audience"]
        
        # In-memory storage (use database in production)
        self.authorization_codes = {}
        self.access_tokens = {}
        
        # Use client configurations from auth_config.py
        self.clients = {}
        valid_clients = get_valid_clients_cached()
        for client_id, client_secret in valid_clients.items():
            if client_id == "vscode-mcp-client":
                self.clients[client_id] = {
                    "client_secret": client_secret,
                    "redirect_uris": [
                        "vscode://vscode.github-authentication/did-authenticate",
                        *get_callback_urls(),
                    ],
                    "grant_types": ["authorization_code", "refresh_token", "client_credentials"],
                    "response_types": ["code"],
                    "scopes": ["flight:read", "flight:write", "booking:manage"]
                }
            elif client_id == "vg-desktop-client":
                self.clients[client_id] = {
                    "client_secret": client_secret,
                    "redirect_uris": get_callback_urls(),
                    "grant_types": ["authorization_code", "refresh_token", "client_credentials"],
                    "response_types": ["code"],
                    "scopes": ["read", "write"]
                }
            else:
                # Default configuration for other clients
                self.clients[client_id] = {
                    "client_secret": client_secret,
                    "redirect_uris": get_callback_urls(),
                    "grant_types": ["authorization_code", "refresh_token", "client_credentials"],
                    "response_types": ["code"],
                    "scopes": ["read", "write"]
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
        valid_clients = get_valid_clients_cached()
        if client_id not in valid_clients:
            logger.error(f"Unknown client_id: {client_id}")
            return False
        
        if client_secret and valid_clients[client_id] != client_secret:
            logger.error(f"Invalid client_secret for client_id: {client_id}")
            return False
            
        logger.info(f"✅ Client verified: {client_id}")
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
        # Create token with configuration-based resource URL
        from ..config.auth_config import AUTH_CONFIG
        token_data = {
            "sub": "demo-user",
            "client_id": client_id,
            "scope": code_data["scope"],
            "resource": AUTH_CONFIG.get("resource_server", "http://localhost:8000")
        }
        
        access_token = self.create_access_token(token_data)
        
        # Log token generation
        logger.info(f"Access token generated for {token_data.get('sub', 'unknown')}")
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f"Generated token: {access_token}")
            logger.debug(f"Token data: {token_data}")
        
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
    
    @app.get("/")
    async def root():
        """Root endpoint - OAuth server status"""
        return {
            "service": "VG OAuth 2.1 Authorization Server",
            "version": "1.0.0",
            "system": "VG_FLIGHTMCP_2024",
            "developer": "Vishal Gupta",
            "status": "running",
            "endpoints": {
                "authorization": "/oauth/authorize",
                "token": "/oauth/token",
                "introspection": "/oauth/introspect",
                "metadata": "/.well-known/oauth-authorization-server",
                "jwks": "/.well-known/jwks.json"
            },
            "demo_credentials": {
                "username": "demo-user",
                "password": "demo-pass"
            },
            "supported_clients": list(oauth_server.clients.keys())
        }

    @app.get("/health")
    async def health():
        """Health check endpoint"""
        return {
            "status": "healthy",
            "service": "OAuth Authorization Server",
            "system": "VG_FLIGHTMCP_2024",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    @app.get("/.well-known/oauth-authorization-server")
    async def authorization_server_metadata():
        """OAuth 2.0 Authorization Server Metadata (RFC 8414)"""
        base_url = get_auth_server_url()
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
        request: Request,
        response_type: str,
        client_id: str,
        redirect_uri: str,
        scope: str = "read",
        state: Optional[str] = None,
        code_challenge: Optional[str] = None,
        code_challenge_method: Optional[str] = None,
        resource: Optional[str] = None
    ):
        """Authorization endpoint - shows login page"""
        log_request(request, "/oauth/authorize", f"client_id={client_id}, scope={scope}")
        
        if not oauth_server.verify_client(client_id):
            logger.error(f"Authorization failed: Invalid client {client_id}")
            raise HTTPException(status_code=400, detail="Invalid client")
        
        # For demo purposes, show a simple login page
        login_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>VG Flight Booking - OAuth Login</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
                .container {{ max-width: 500px; margin: 50px auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                .header {{ text-align: center; margin-bottom: 30px; }}
                .brand {{ color: #007bff; font-size: 24px; font-weight: bold; }}
                .subtitle {{ color: #666; margin: 10px 0; }}
                .form-group {{ margin: 20px 0; }}
                label {{ display: block; margin-bottom: 5px; font-weight: bold; }}
                input[type="text"], input[type="password"] {{ width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px; font-size: 16px; }}
                .btn {{ background: #007bff; color: white; padding: 12px 30px; border: none; border-radius: 5px; font-size: 16px; cursor: pointer; width: 100%; }}
                .btn:hover {{ background: #0056b3; }}
                .scope {{ background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0; }}
                .client-info {{ background: #e7f3ff; padding: 15px; border-radius: 5px; margin: 20px 0; }}
                .watermark {{ text-align: center; color: #999; font-size: 12px; margin-top: 20px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div class="brand">✈️ VG Flight Booking</div>
                    <div class="subtitle">OAuth 2.0 Authentication</div>
                </div>
                
                <div class="client-info">
                    <strong>Application:</strong> {client_id}<br>
                    <strong>Redirect URI:</strong> {redirect_uri}
                </div>
                
                <div class="scope">
                    <strong>Requested Permissions:</strong><br>
                    🔍 Search flights<br>
                    ✈️ Create bookings<br>
                    📋 Access booking history
                </div>
                
                <form method="post" action="/oauth/authorize/approve">
                    <input type="hidden" name="client_id" value="{client_id}">
                    <input type="hidden" name="redirect_uri" value="{redirect_uri}">
                    <input type="hidden" name="scope" value="{scope}">
                    <input type="hidden" name="state" value="{state or ''}">
                    <input type="hidden" name="code_challenge" value="{code_challenge or ''}">
                    <input type="hidden" name="code_challenge_method" value="{code_challenge_method or ''}">
                    
                    <div class="form-group">
                        <label for="username">Username:</label>
                        <input type="text" id="username" name="username" value="demo-user" required>
                    </div>
                    
                    <div class="form-group">
                        <label for="password">Password:</label>
                        <input type="password" id="password" name="password" value="demo-pass" required>
                    </div>
                    
                    <button type="submit" class="btn">🔐 Authorize VG Flight Booking</button>
                </form>
                
                <div class="watermark">
                    Powered by VG_FLIGHTMCP_2024 | Secure OAuth 2.0
                </div>
            </div>
        </body>
        </html>
        """
        
        return HTMLResponse(login_html)
    
    @app.post("/oauth/authorize/approve")
    async def authorize_approve(
        request: Request,
        client_id: str = Form(...),
        redirect_uri: str = Form(...),
        scope: str = Form(...),
        username: str = Form(...),
        password: str = Form(...),
        state: Optional[str] = Form(None),
        code_challenge: Optional[str] = Form(None),
        code_challenge_method: Optional[str] = Form(None)
    ):
        """Handle authorization approval"""
        log_request(request, "/oauth/authorize/approve", f"user={username}, client_id={client_id}")
        
        logger.info(f"📋 Authorization approval request:")
        logger.info(f"   👤 Username: {username}")
        logger.info(f"   🏢 Client ID: {client_id}")
        logger.info(f"   🔗 Redirect URI: {redirect_uri}")
        logger.info(f"   🔍 Scope: {scope}")
        logger.info(f"   🏷️  State: {state}")
        logger.info(f"   🔒 Code Challenge: {'Yes' if code_challenge else 'No'}")
        
        # Verify client
        if not oauth_server.verify_client(client_id):
            logger.error(f"❌ Invalid client_id: {client_id}")
            raise HTTPException(status_code=400, detail=f"Invalid client: {client_id}")
        
        # Simple credential check (in real app, use proper authentication)
        if username != "demo-user" or password != "demo-pass":
            logger.error(f"❌ Invalid credentials for user {username}")
            raise HTTPException(status_code=400, detail="Invalid credentials")
        
        # Generate authorization code
        auth_code = oauth_server.generate_authorization_code(
            client_id, redirect_uri, scope, code_challenge, code_challenge_method
        )
        
        logger.info(f"✅ Authorization approved for user {username}")
        logger.info(f"🎫 Authorization code generated: {auth_code[:8]}...")
        logger.info(f"🏷️  System: VG_FLIGHTMCP_2024")
        
        # Build redirect URL
        redirect_params = {"code": auth_code}
        if state:
            redirect_params["state"] = state
        
        redirect_url = f"{redirect_uri}?" + urllib.parse.urlencode(redirect_params)
        
        logger.info(f"🔄 Redirecting to: {redirect_url}")
        return RedirectResponse(redirect_url)
    
    @app.post("/oauth/token")
    async def token(
        request: Request,
        grant_type: str = Form(...),
        client_id: str = Form(...),
        client_secret: str = Form(...),
        code: Optional[str] = Form(None),
        redirect_uri: Optional[str] = Form(None),
        code_verifier: Optional[str] = Form(None),
        scope: Optional[str] = Form(None),
        resource: Optional[str] = Form(None)
    ):
        """Token endpoint - supports authorization_code and client_credentials"""
        log_request(request, "/oauth/token", f"grant_type={grant_type}, client_id={client_id}")
        
        logger.info("🎫 Token exchange request received")
        logger.info(f"   📋 Grant Type: {grant_type}")
        logger.info(f"   👤 Client ID: {client_id}")
        logger.info(f"   🏷️  System: VG_FLIGHTMCP_2024")
        
        # Verify client credentials
        if not oauth_server.verify_client(client_id, client_secret):
            logger.error(f"❌ Invalid client credentials: {client_id}")
            raise HTTPException(status_code=401, detail="Invalid client credentials")
        
        if grant_type == "authorization_code":
            # Authorization Code Flow
            if not code or not redirect_uri:
                logger.error("Missing code or redirect_uri for authorization_code flow")
                raise HTTPException(status_code=400, detail="Missing code or redirect_uri")
                
            logger.info(f"   🔐 Authorization Code: {code[:8]}...")
            logger.info(f"   🔗 Redirect URI: {redirect_uri}")
            logger.info(f"   🔒 PKCE Verifier: {'Yes' if code_verifier else 'No'}")
            
            try:
                token_response = oauth_server.exchange_code_for_token(
                    code, client_id, client_secret, redirect_uri, code_verifier
                )
                logger.info("✅ Authorization code exchanged successfully")
                return token_response
            except Exception as e:
                logger.error(f"Token exchange failed: {str(e)}")
                raise
                
        elif grant_type == "client_credentials":
            # Client Credentials Flow
            logger.info("   🔑 Client Credentials Flow")
            logger.info(f"   🔍 Scope: {scope or 'default'}")
            
            try:
                # Generate token for client credentials
                token_scope = scope or "read write"
                token_data = {
                    "sub": client_id,
                    "client_id": client_id,
                    "scope": token_scope,
                    "token_type": "Bearer"
                }
                
                access_token = oauth_server.create_access_token(token_data)
                
                response_data = {
                    "access_token": access_token,
                    "token_type": "Bearer",
                    "expires_in": 3600,
                    "scope": token_scope
                }
                
                logger.info("✅ Client credentials token generated successfully")
                return response_data
                
            except Exception as e:
                logger.error(f"Client credentials token generation failed: {e}")
                raise HTTPException(status_code=500, detail="Token generation failed")
        else:
            logger.error(f"Unsupported grant type: {grant_type}")
            raise HTTPException(status_code=400, detail=f"Unsupported grant_type: {grant_type}")
    
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


def run_oauth_server(host: str = "localhost", port: int = None):
    """Run the OAuth server for programmatic access"""
    config = get_auth_server_config().copy()
    config["host"] = host
    config["port"] = port or config["port"]
    
    oauth_server = OAuthServer(config)
    app = create_oauth_app(oauth_server)
    
    logger.info("🚀 Starting VG OAuth Authorization Server")
    logger.info(f"🌐 Host: {host}:{port}")
    logger.info("🏷️  System: VG_FLIGHTMCP_2024")
    
    uvicorn.run(app, host=host, port=port, log_level="warning")


if __name__ == "__main__":
    main()

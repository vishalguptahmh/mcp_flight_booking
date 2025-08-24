"""
OAuth 2.1 Authentication Configuration
"""

import os

# OAuth Server Configuration
OAUTH_CONFIG = {
    "authorization_server": os.getenv("OAUTH_AUTH_SERVER", "http://localhost:9000"),
    "jwt_secret": os.getenv("JWT_SECRET", "mock-secret-key-for-development"),
    "expected_audience": os.getenv("OAUTH_AUDIENCE", "https://mcp.example.com"),
    "expected_issuer": os.getenv("OAUTH_ISSUER", "https://auth.example.com"),
    "algorithm": "HS256",
    "token_expiry_hours": int(os.getenv("TOKEN_EXPIRY_HOURS", "1")),
}

# OAuth Server Settings
AUTH_SERVER_CONFIG = {
    "host": os.getenv("AUTH_HOST", "localhost"),
    "port": int(os.getenv("AUTH_PORT", "9000")),
    "secret_key": os.getenv("JWT_SECRET", "mock-secret-key-for-development"),
    "algorithm": "HS256",
    "issuer": os.getenv("OAUTH_ISSUER", "https://auth.example.com"),
    "audience": os.getenv("OAUTH_AUDIENCE", "https://mcp.example.com"),
}

# Client Configuration
OAUTH_CLIENT_CONFIG = {
    "client_id": "mcp-client",
    "client_secret": "mcp-client-secret",
    "redirect_uri": os.getenv("OAUTH_REDIRECT_URI", "http://localhost:3000/oauth/callback"),
    "oob_redirect_uri": "urn:ietf:wg:oauth:2.0:oob",  # Keep OOB for CLI/testing
    "scope": "read write",
    "use_oob_flow": os.getenv("USE_OOB_FLOW", "false").lower() == "true",
}

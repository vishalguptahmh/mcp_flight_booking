"""
OAuth 2.1 Authentication Configuration
"""

import os

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

def _get_required_env(key: str) -> str:
    """Get required environment variable or raise error with helpful message."""
    value = os.getenv(key)
    if not value:
        raise ValueError(
            f"{key} environment variable is required. "
            f"Please copy .env.example to .env and set your values."
        )
    return value

# OAuth Server Configuration - lazy loaded
def get_oauth_config():
    """Get OAuth configuration with lazy initialization"""
    return {
        "authorization_server": os.getenv("OAUTH_AUTH_SERVER", "http://localhost:9000"),
        "resource_server": os.getenv("RESOURCE_SERVER", "http://localhost:8000"),
        "jwt_secret": _get_required_env("JWT_SECRET"),
        "expected_audience": os.getenv("OAUTH_AUDIENCE", "https://mcp.example.com"),
        "expected_issuer": os.getenv("OAUTH_ISSUER", "https://auth.example.com"),
        "algorithm": "HS256",
        "token_expiry_hours": int(os.getenv("TOKEN_EXPIRY_HOURS", "1")),
    }

# OAuth Server Configuration - lazy loaded
def get_auth_server_config():
    """Get auth server configuration with lazy initialization"""
    return {
        "host": os.getenv("AUTH_HOST", "localhost"),
        "port": int(os.getenv("AUTH_PORT", "9000")),
        "secret_key": _get_required_env("JWT_SECRET"),
        "algorithm": "HS256",
        "issuer": os.getenv("OAUTH_ISSUER", "https://auth.example.com"),
        "audience": os.getenv("OAUTH_AUDIENCE", "https://mcp.example.com"),
    }

# Backward compatibility with caching
_oauth_config_cache = None
_auth_server_config_cache = None

OAUTH_CONFIG = None  # Will be initialized lazily
AUTH_SERVER_CONFIG = None  # Will be initialized lazily

def _ensure_configs_loaded():
    """Ensure configurations are loaded"""
    global OAUTH_CONFIG, AUTH_SERVER_CONFIG, _oauth_config_cache, _auth_server_config_cache
    if OAUTH_CONFIG is None:
        OAUTH_CONFIG = get_oauth_config()
        _oauth_config_cache = OAUTH_CONFIG
    if AUTH_SERVER_CONFIG is None:
        AUTH_SERVER_CONFIG = get_auth_server_config()
        _auth_server_config_cache = AUTH_SERVER_CONFIG

# Client callback configuration
CALLBACK_CONFIG = {
    "host": os.getenv("CALLBACK_HOST", "localhost"),
    "port": int(os.getenv("CALLBACK_PORT", "3000")),
    "scheme": os.getenv("CALLBACK_SCHEME", "http"),
}

# URL builders for consistency
def get_auth_server_url():
    """Get the complete OAuth server URL"""
    _ensure_configs_loaded()
    return f"http://{AUTH_SERVER_CONFIG['host']}:{AUTH_SERVER_CONFIG['port']}"

def get_callback_url(path="/callback"):
    """Get the complete callback URL"""
    return f"{CALLBACK_CONFIG['scheme']}://{CALLBACK_CONFIG['host']}:{CALLBACK_CONFIG['port']}{path}"

def get_callback_urls():
    """Get list of valid callback URLs for OAuth clients"""
    base_url = f"{CALLBACK_CONFIG['scheme']}://{CALLBACK_CONFIG['host']}"
    return [
        f"{base_url}:{CALLBACK_CONFIG['port']}/callback",
        f"{base_url}:{CALLBACK_CONFIG['port'] + 1}/callback",
        f"{base_url}:{CALLBACK_CONFIG['port'] + 2}/callback",
        "urn:ietf:wg:oauth:2.0:oob"  # Out-of-band flow
    ]

# Client Configuration - lazy loaded
def get_oauth_client_config():
    """Get OAuth client configuration with lazy initialization"""
    return {
        "client_id": os.getenv("MCP_CLIENT_ID", "mcp-client"),
        "client_secret": _get_required_env("MCP_CLIENT_SECRET"),
        "redirect_uri": os.getenv("OAUTH_REDIRECT_URI", ""),  # Will be set dynamically
        "oob_redirect_uri": "urn:ietf:wg:oauth:2.0:oob",  # Keep OOB for CLI/testing
        "scope": "read write",
        "use_oob_flow": os.getenv("USE_OOB_FLOW", "false").lower() == "true",
    }

# Desktop Client Configuration (VS Code style) - lazy loaded
def get_desktop_client_config():
    """Get desktop client configuration with lazy initialization"""
    config = {
        "client_id": os.getenv("VSCODE_CLIENT_ID", "vscode-mcp-client"),
        "client_secret": _get_required_env("VSCODE_CLIENT_SECRET"),
        "redirect_uri": "",  # Will be set dynamically
        "scope": "read write",
    }
    if not config["redirect_uri"]:
        config["redirect_uri"] = get_callback_url()
    return config

# Backward compatibility
OAUTH_CLIENT_CONFIG = {}
DESKTOP_CLIENT_CONFIG = {}

# Set dynamic redirect URIs after function definitions
def _initialize_redirect_uris():
    """Initialize redirect URIs lazily to avoid circular imports"""
    oauth_config = get_oauth_client_config()
    if not oauth_config["redirect_uri"]:
        oauth_config["redirect_uri"] = get_callback_url("/oauth/callback")

# Backward compatibility alias
def get_auth_config():
    """Get auth config (alias for oauth config)"""
    return get_oauth_config()

AUTH_CONFIG = None  # Will be initialized lazily

# Valid OAuth clients for the server  
def get_valid_clients():
    """Get valid OAuth clients with lazy initialization"""
    return {
        os.getenv("MCP_CLIENT_ID", "mcp-client"): _get_required_env("MCP_CLIENT_SECRET"),
        os.getenv("VG_CLIENT_ID", "mcp-client-vg"): _get_required_env("VG_CLIENT_SECRET"), 
        "vg-desktop-client": os.getenv("VG_DESKTOP_CLIENT_SECRET", "dev-vg-desktop-secret-123"),
        os.getenv("VSCODE_CLIENT_ID", "vscode-mcp-client"): _get_required_env("VSCODE_CLIENT_SECRET"),
        os.getenv("CLAUDE_DESKTOP_CLIENT_ID", "claude-desktop-client"): _get_required_env("CLAUDE_DESKTOP_CLIENT_SECRET"),
    }

# For backward compatibility, initialize lazily
_valid_clients_cache = None

def get_valid_clients_cached():
    """Get valid clients with caching"""
    global _valid_clients_cache
    if _valid_clients_cache is None:
        _valid_clients_cache = get_valid_clients()
    return _valid_clients_cache

# Backward compatibility - but this will only work if env vars are set
VALID_CLIENTS = {}

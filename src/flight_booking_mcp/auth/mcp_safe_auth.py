"""
Simple MCP-compatible VS Code authentication
"""

import secrets
import hashlib
import base64
import urllib.parse
import requests
from typing import Dict

# Import configuration
from ..config.auth_config import get_auth_server_url, get_callback_url, get_desktop_client_config

def mcp_safe_vscode_auth() -> Dict[str, str]:
    """
    MCP-safe VS Code authentication that works in async environments
    """
    # Use configuration values
    desktop_config = get_desktop_client_config()
    client_id = desktop_config["client_id"]
    client_secret = desktop_config["client_secret"]
    oauth_server_url = get_auth_server_url()
    scope = desktop_config["scope"]
    callback_url = get_callback_url()
    
    # Generate PKCE challenge
    code_verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode('utf-8').rstrip('=')
    code_challenge = base64.urlsafe_b64encode(
        hashlib.sha256(code_verifier.encode('utf-8')).digest()
    ).decode('utf-8').rstrip('=')
    state = secrets.token_urlsafe(32)
    
    # Build authorization URL
    auth_params = {
        "response_type": "code",
        "client_id": client_id,
        "redirect_uri": callback_url,
        "scope": scope,
        "state": state,
        "code_challenge": code_challenge,
        "code_challenge_method": "S256"
    }
    
    auth_url = f"{oauth_server_url}/oauth/authorize?" + urllib.parse.urlencode(auth_params)
    
    # Get demo token using client credentials
    token_url = f"{oauth_server_url}/oauth/token"
    token_data = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret,
        "scope": scope
    }
    
    try:
        response = requests.post(
            token_url,
            data=token_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=5
        )
        
        if response.status_code == 200:
            token_info = response.json()
            return {
                "status": "success",
                "access_token": token_info["access_token"],
                "token_type": token_info.get("token_type", "Bearer"),
                "expires_in": str(token_info.get("expires_in", 3600)),
                "scope": token_info.get("scope", scope),
                "client_id": client_id,
                "auth_method": "vscode_oauth_demo",
                "provider": "VG_FlightMCP_2024",
                "authorization_url": auth_url,
                "demo_credentials": {
                    "username": "demo-user",
                    "password": "demo-pass"
                }
            }
        else:
            return {"error": f"Token request failed: {response.status_code} - {response.text}"}
    except Exception as e:
        return {"error": f"Authentication service unavailable: {str(e)}"}

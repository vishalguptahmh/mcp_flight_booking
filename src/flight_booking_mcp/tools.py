"""
MCP Tools Definitions
Author: Vishal Gupta
Created: August 2024
Watermark: VG_FLIGHTMCP_2024
Clean separation of MCP tool definitions from business logic
OAuth-protected tools for secure access
"""

from fastmcp import FastMCP
from functools import wraps
import asyncio
import logging
import os
import subprocess
import sys
from datetime import datetime
from typing import Dict, Any
from pathlib import Path

# Import configuration helpers
from .config.auth_config import get_auth_server_url, get_callback_url
from .auth.token_validator import get_token_validator

# Configure MCP Tools logging
log_dir = os.path.dirname(os.path.abspath(__file__))
mcp_log_file = os.path.join(log_dir, 'mcp_tools.log')

logging.basicConfig(
    level=logging.INFO,
    format='🛠️  %(asctime)s - %(name)s - [%(levelname)s] - %(message)s',
    handlers=[
        logging.FileHandler(mcp_log_file),
        logging.StreamHandler()
    ]
)

mcp_logger = logging.getLogger("VG_MCP_Tools")

## Remove top-level import to avoid circular import

def require_mcp_auth(func):
    """Decorator to require OAuth authentication for MCP tools"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        mcp_logger.info(f"🔐 Checking authentication for MCP tool: {func.__name__}")
        
        # Check if we have a stored authentication token
        # In MCP context, we need to check for stored token or require authentication
        try:
            # For now, we'll implement a basic check
            # In a real implementation, you'd get the token from MCP context or environment
            auth_token = os.environ.get('MCP_AUTH_TOKEN')
            
            if not auth_token:
                mcp_logger.error(f"❌ No authentication token found for {func.__name__}")
                return {
                    "error": "Authentication required",
                    "message": "Please authenticate first using the authenticate_with_oauth2 tool",
                    "required_action": "Call authenticate_with_oauth2() to get access token",
                    "_vg_security": {
                        "authentication_required": True,
                        "tool_protected": True,
                        "provider": "VG_FLIGHTMCP_2024"
                    }
                }
            
            # Validate the token
            try:
                token_validator = get_token_validator()
                token_data = token_validator.verify_token(auth_token)
                mcp_logger.info(f"✅ Authentication successful for {func.__name__}")
                mcp_logger.info(f"   👤 User: {token_data.get('sub', 'unknown')}")
                
                # Don't pass token data to the function - just proceed with original args/kwargs
                
            except Exception as token_error:
                mcp_logger.error(f"❌ Token validation failed for {func.__name__}: {token_error}")
                return {
                    "error": "Invalid or expired authentication token",
                    "message": "Please re-authenticate using the authenticate_with_oauth2 tool",
                    "required_action": "Call authenticate_with_oauth2() to refresh access token",
                    "_vg_security": {
                        "token_validation_failed": True,
                        "error_details": str(token_error),
                        "provider": "VG_FLIGHTMCP_2024"
                    }
                }
            
        except Exception as auth_error:
            mcp_logger.error(f"❌ Authentication check failed for {func.__name__}: {auth_error}")
            return {
                "error": "Authentication system error",
                "message": "Unable to verify authentication",
                "required_action": "Contact system administrator or try authenticate_with_oauth2()",
                "_vg_security": {
                    "auth_system_error": True,
                    "error_details": str(auth_error),
                    "provider": "VG_FLIGHTMCP_2024"
                }
            }
        
        # Call the original function with authentication confirmed
        return func(*args, **kwargs)
    
    return wrapper


def log_tool_access(func):
    """Decorator to log tool access and add VG system identification"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        mcp_logger.info(f"🔧 VG Tool accessed: {func.__name__}")
        mcp_logger.debug(f"📝 Args: {args}, Kwargs: {kwargs}")
        
        try:
            result = func(*args, **kwargs)
            
            mcp_logger.info(f"✅ VG Tool execution successful: {func.__name__}")
            mcp_logger.info(f"   📤 Result type: {type(result).__name__}")
            
            # Add VG system identification (subtle watermarking)
            if isinstance(result, dict):
                result["_vg_system"] = {
                    "provider": "VG_FlightMCP",
                    "version": "2024.1",
                    "developer": "Vishal Gupta"
                }
                mcp_logger.info(f"   🔐 Auth metadata added to response")
            
            mcp_logger.info("-" * 60)
            return result
            
        except Exception as e:
            mcp_logger.error(f"❌ VG Tool execution failed: {func.__name__}")
            mcp_logger.error(f"   🚨 Error: {str(e)}")
            mcp_logger.error("-" * 60)
            
            return {
                "error": str(e),
                "_vg_system": {
                    "provider": "VG_FlightMCP",
                    "error_context": "VG system error",
                    "developer": "Vishal Gupta"
                }
            }
    return wrapper


def register_mcp_tools(mcp_server: FastMCP):
    """Register all OAuth-protected MCP tools with the server"""
    
    @mcp_server.tool()
    @require_mcp_auth
    @log_tool_access
    def search_flights(origin: str, destination: str, date: str = "2024-12-01") -> dict:
        """
        Search for flights between two airports
        � VG Flight Search System
        
        Args:
            origin: Origin airport code (e.g., 'PNQ', 'DEL')
            destination: Destination airport code
            date: Travel date (YYYY-MM-DD)
        
        Returns:
            Flight search results with pricing and schedules
        """
        import importlib
        import sys
        
        # Force reload to pick up latest changes
        module_name = 'flight_booking_mcp.services.flight_service'
        if module_name in sys.modules:
            importlib.reload(sys.modules[module_name])
        
        from .services.flight_service import flight_service
        
        # Add VG system identification
        result = flight_service.search_flights(origin, destination, date)
        result["_vg_metadata"] = {
            "search_provider": "VG Flight Search",
            "developer": "Vishal Gupta",
            "system_id": "VG_FLIGHTMCP_2024"
        }
        return result
    
    @mcp_server.tool()
    @require_mcp_auth
    @log_tool_access  
    def create_booking(flight_id: str, passenger_name: str, email: str = "passenger@example.com") -> dict:
        """
        Create a flight booking
        ✈️ VG Booking System
        
        Args:
            flight_id: Flight ID from search results (e.g., 'VG123')
            passenger_name: Passenger full name
            email: Passenger email address
        
        Returns:
            Booking confirmation with VG-prefixed booking ID
        """
        import importlib
        import sys
        
        # Force reload to pick up latest changes
        module_name = 'flight_booking_mcp.services.flight_service'
        if module_name in sys.modules:
            importlib.reload(sys.modules[module_name])
        
        from .services.flight_service import flight_service
        
        # Validate flight ID format (must start with VG for our watermarked flights)
        if not flight_id.startswith('VG'):
            return {
                "error": f"Invalid flight ID format: {flight_id}. Must be VG-prefixed flight.",
                "_vg_system": {
                    "validation_failed": True,
                    "system_id": "VG_FLIGHTMCP_2024",
                    "developer": "Vishal Gupta"
                }
            }
        
        result = flight_service.create_booking(flight_id, passenger_name, email)
        result["_vg_metadata"] = {
            "booking_system": "VG FlightMCP",
            "developer": "Vishal Gupta"
        }
        return result
    
    @mcp_server.tool()
    @require_mcp_auth
    @log_tool_access
    def get_user_bookings(email: str = "passenger@example.com") -> dict:
        """
        Get user's flight bookings
        � VG Booking Management
        
        Args:
            email: User email address
            
        Returns:
            List of user bookings
        """
        from .services.flight_service import flight_service
        import importlib
        import sys
        
        # Force reload to pick up latest changes
        if 'flight_booking_mcp.services.flight_service' in sys.modules:
            importlib.reload(sys.modules['flight_booking_mcp.services.flight_service'])
            from .services.flight_service import flight_service
        
        bookings = flight_service.get_bookings(email)
        return {
            "user_email": email,
            "bookings": bookings,
            "total_bookings": len(bookings),
            "_vg_metadata": {
                "data_provider": "VG Booking System",
                "access_type": "User bookings",
                "developer": "Vishal Gupta"
            }
        }
    
    @mcp_server.tool()
    @require_mcp_auth
    @log_tool_access
    def get_available_airports() -> dict:
        """
        Get list of all available airports
        � VG Airport Database
        
        Returns:
            Dictionary of available airports with details
        """
        from .services.flight_service import flight_service
        import importlib
        import sys
        
        # Force reload to pick up latest changes
        if 'flight_booking_mcp.services.flight_service' in sys.modules:
            importlib.reload(sys.modules['flight_booking_mcp.services.flight_service'])
            from .services.flight_service import flight_service
        
        airports = flight_service.get_airports()
        return {
            "airports": airports,
            "total_airports": len(airports),
            "_vg_metadata": {
                "data_source": "VG Airport Database",
                "coverage": "29 airports",
                "developer": "Vishal Gupta"
            }
        }
    
    @mcp_server.tool()
    @log_tool_access
    def authenticate_with_oauth2() -> dict:
        """
        Authenticate with VG Flight Booking using OAuth 2.0

        This triggers an OAuth 2.0 authorization popup, then opens the browser for OAuth
        authentication - exactly like VS Code's GitHub authentication flow.
        
        Returns:
            Authentication status and popup/browser flow details
        """
        try:
            from .auth.mcp_safe_auth import mcp_safe_vscode_auth
            
            mcp_logger.info("Starting VS Code-style authentication with popup")
            
            # Run MCP-safe authentication
            result = mcp_safe_vscode_auth()
            
            if "error" in result:
                return {
                    "error": result["error"],
                    "status": "failed",
                    "message": "VS Code authentication failed",
                    "fallback": {
                        "message": "Manual authentication steps:",
                        "steps": [
                            f"1. OAuth server running on {get_auth_server_url()}",
                            "2. Visit authorization URL in browser",
                            "3. Login with demo-user / demo-pass",
                            "4. Complete OAuth flow manually"
                        ]
                    },
                    "_vg_system": {
                        "provider": "VG_FlightMCP",
                        "version": "2024.1",
                        "developer": "Vishal Gupta"
                    }
                }
            
            # Store the access token in environment for MCP tools to use
            access_token = result.get("access_token")
            if access_token:
                os.environ['MCP_AUTH_TOKEN'] = access_token
                mcp_logger.info("✅ Authentication token stored for MCP tools")
            else:
                mcp_logger.warning("⚠️ No access token received from authentication")
            
            return {
                "status": "popup_shown",
                "message": "🔐 VS Code Authorization Popup Displayed", 
                "description": "Browser authentication window opened",
                "authorization_url": result["authorization_url"],
                "demo_credentials": result["demo_credentials"],
                "flow_details": {
                    "access_token": result["access_token"],
                    "token_type": result["token_type"],
                    "expires_in": result["expires_in"],
                    "scope": result["scope"],
                    "auth_method": result["auth_method"],
                    "provider": result["provider"]
                },
                "instructions": [
                    "� VS Code Authentication Flow:",
                    "",
                    "1. 📱 VS Code shows authorization popup",
                    "2. 🌐 Browser opens VG Flight Booking OAuth page", 
                    f"3. 🔗 Visit: {result['authorization_url']}",
                    "4. 🔑 Login with demo credentials:",
                    "   - Username: demo-user",
                    "   - Password: demo-pass",
                    "5. 🔐 Click 'Authorize VG Flight Booking'",
                    "6. ✅ Browser redirects back to VS Code",
                    "7. 🎫 Authentication token stored securely",
                    "",
                    "✨ Same experience as GitHub authentication in VS Code!",
                    "",
                    "🎉 Demo token already generated for immediate API access!"
                ],
                "_vg_auth": {
                    "provider": "VG_VSCode_OAuth",
                    "flow_type": "popup_browser_redirect", 
                    "system": "VG_FLIGHTMCP_2024",
                    "developer": "Vishal Gupta"
                }
            }
            
        except Exception as e:
            mcp_logger.error(f"VS Code authentication failed: {e}")
            return {
                "error": str(e),
                "status": "failed",
                "message": "VS Code authentication popup failed",
                "fallback": {
                    "message": "Start OAuth servers manually:",
                    "steps": [
                        "1. python -m flight_booking_mcp.auth.oauth_server",
                        f"2. Visit {get_auth_server_url()}/oauth/authorize",
                        "3. Login with demo-user / demo-pass"
                    ]
                },
                "_vg_system": {
                    "provider": "VG_FlightMCP",
                    "error_type": "vscode_auth_failed",
                    "developer": "Vishal Gupta"
                }
            }

    return mcp_server

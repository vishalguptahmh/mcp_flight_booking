#!/usr/bin/env python3
"""
Flight Booking MCP Server v2.1
Clean implementation following Single Responsibility Principle
Updated: 2024-12-19 - Booking functionality verified
"""

import asyncio
import uvicorn
import time
import logging
import os
from datetime import datetime
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from .models import SearchFlightsRequest, CreateBookingRequest
from typing import Optional
from fastmcp import FastMCP
from .config.mcp_config import MCP_CONFIG
from .config.auth_config import get_auth_server_url, get_callback_url
from .auth.token_validator import verify_oauth_token
from .services import flight_service
from .tools import register_mcp_tools
from .resources import register_mcp_resources

# Configure MCP Server logging
log_dir = os.path.dirname(os.path.abspath(__file__))
server_log_file = os.path.join(log_dir, 'mcp_server.log')

logging.basicConfig(
    level=logging.INFO,
    format='🖥️  %(asctime)s - %(name)s - [%(levelname)s] - %(message)s',
    handlers=[
        logging.FileHandler(server_log_file),
        logging.StreamHandler()
    ]
)

server_logger = logging.getLogger("VG_MCP_Server")

# Pydantic models for request bodies

class MCPServer:
    """MCP Server with OAuth protection"""
    
    def __init__(self, config=None):
        self.config = config or MCP_CONFIG
        self.flight_service = flight_service
    
    def create_stdio_server(self) -> FastMCP:
        """Create MCP server for stdio transport (MCP Studio)"""
        server_logger.info("🔧 Creating MCP Server for stdio transport")
        server_logger.info(f"   🏷️  System: VG_FLIGHTMCP_2024")
        server_logger.info(f"   📋 Server Name: {self.config['server_name']}")
        server_logger.info(f"   ⏰ Timestamp: {datetime.now().isoformat()}")
        
        mcp = FastMCP(self.config["server_name"])
        
        server_logger.info("🛠️  Registering MCP tools...")
        # Register tools and resources
        register_mcp_tools(mcp)
        
        server_logger.info("📚 Registering MCP resources...")
        register_mcp_resources(mcp)
        
        server_logger.info("✅ MCP Server created successfully")
        server_logger.info("-" * 60)
        
        return mcp
    
    def create_oauth_server(self) -> FastAPI:
        """Create FastAPI server with OAuth protection"""
        app = FastAPI(
            title=self.config["server_name"],
            description="OAuth-protected MCP server for flight booking",
            version=self.config["version"]
        )
        
        security = HTTPBearer()
        
        # Public endpoints
        @app.get("/health")
        async def health():
            """Health check endpoint"""
            return {
                "status": "healthy",
                "service": self.config["server_name"],
                "oauth_enabled": True,
                "auth_server": get_auth_server_url(),
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
        
        @app.get("/.well-known/oauth-protected-resource")
        async def oauth_metadata():
            """OAuth Protected Resource Metadata (RFC 9728)"""
            return {
                "resource": "https://mcp.example.com",
                "authorization_servers": ["https://auth.example.com"],
                "scopes_supported": ["read", "write"],
                "bearer_methods_supported": ["header"]
            }
        
        @app.get("/test/public")
        async def test_public():
            """Public test endpoint"""
            return {"message": "🌐 Public endpoint - no OAuth needed"}
        
        # Protected endpoints
        @app.get("/test/protected")
        async def test_protected(token_data: dict = Depends(verify_oauth_token)):
            """Protected test endpoint"""
            return {
                "message": "🔐 OAuth protection working!",
                "user": token_data.get("sub"),
                "client": token_data.get("client_id"),
                "scopes": token_data.get("scope", "").split()
            }
        
        @app.get("/oauth/info")
        async def oauth_info(token_data: dict = Depends(verify_oauth_token)):
            """Get OAuth token information"""
            return {
                "user": token_data.get("sub"),
                "client": token_data.get("client_id"),
                "scopes": token_data.get("scope", "").split(),
                "expires": token_data.get("exp"),
                "issued": token_data.get("iat")
            }
        
        # MCP endpoints
        @app.get("/mcp/airports")
        async def get_airports(token_data: dict = Depends(verify_oauth_token)):
            """Get available airports"""
            try:
                airports = self.flight_service.get_airports()
                return {
                    "airports": airports,
                    "count": len(airports)
                }
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @app.post("/mcp/search-flights")
        async def search_flights(
            request_body: SearchFlightsRequest,
            token_data: dict = Depends(verify_oauth_token)
        ):
            """Search for flights"""
            try:
                result = self.flight_service.search_flights(
                    request_body.origin, 
                    request_body.destination, 
                    request_body.date
                )
                return result
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @app.post("/mcp/create-booking")
        async def create_booking(
            request_body: CreateBookingRequest,
            token_data: dict = Depends(verify_oauth_token)
        ):
            """Create a flight booking"""
            try:
                return self.flight_service.create_booking(
                    request_body.flight_id, 
                    request_body.passenger_name, 
                    request_body.email
                )
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @app.get("/mcp/bookings")
        async def get_bookings(
            token_data: dict = Depends(verify_oauth_token)
        ):
            """Get user's bookings"""
            try:
                # In a real system, you'd get the user ID from the token
                # For now, we'll return all bookings or use a test email
                user_email = token_data.get("sub", "test@example.com")
                bookings = self.flight_service.get_bookings(user_email)
                return {"bookings": bookings}
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        return app


# Global server instance
mcp_server = MCPServer()


def run_stdio_mode():
    """Run MCP server in stdio mode (Claude Desktop)"""
    server_logger.info("🚀 Starting MCP Server in stdio mode")
    server_logger.info(f"   🏷️  System: VG_FLIGHTMCP_2024")
    server_logger.info(f"   📡 Transport: stdio (Claude Desktop)")
    server_logger.info(f"   ⏰ Timestamp: {datetime.now().isoformat()}")
    server_logger.info("-" * 60)
    
    mcp_server = MCPServer()
    server = mcp_server.create_stdio_server()
    
    server_logger.info("🚀 MCP Server starting stdio transport...")
    server.run(transport="stdio")


def run_oauth_mode(host="localhost", port=8000):
    """Run MCP server in OAuth HTTP mode"""
    import uvicorn
    
    print("🔐 Starting OAuth-protected Flight Booking MCP Server...")
    print("=" * 55)
    print(f"📍 Server URL: http://{host}:{port}")
    print(f"🔑 OAuth Auth Server: {get_auth_server_url()}")
    print()
    print("🌐 Public endpoints:")
    print(f"   • Health: http://{host}:{port}/health")
    print(f"   • OAuth metadata: http://{host}:{port}/.well-known/oauth-protected-resource")
    print(f"   • Test public: http://{host}:{port}/test/public")
    print()
    print("🔐 Protected endpoints (require OAuth token):")
    print(f"   • Test protected: http://{host}:{port}/test/protected")
    print(f"   • OAuth info: http://{host}:{port}/oauth/info")
    print(f"   • Airports: http://{host}:{port}/mcp/airports")
    print(f"   • Search flights: POST http://{host}:{port}/mcp/search-flights")
    print(f"   • Create booking: POST http://{host}:{port}/mcp/create-booking")
    print(f"   • Get bookings: http://{host}:{port}/mcp/bookings")
    print()
    print("🚀 Getting started:")
    print("   1. Get token: uv run python client/token_client.py")
    print(f"   2. Test: curl -H 'Authorization: Bearer TOKEN' http://{host}:{port}/test/protected")
    print(f"   3. Web interface: {get_callback_url()}")
    print()
    
    app = mcp_server.create_oauth_server()
    uvicorn.run(app, host=host, port=port, log_level="info")


if __name__ == "__main__":
    import sys
    
    server_logger.info("🚀 Flight Booking MCP Server - Direct Execution")
    server_logger.info(f"   🏷️  Watermark: VG_FLIGHTMCP_2024")
    server_logger.info(f"   📋 Args: {sys.argv}")
    
    if len(sys.argv) > 1:
        mode = sys.argv[1]
        server_logger.info(f"   🎯 Mode specified: {mode}")
        
        if mode == "--studio":
            server_logger.info("📡 Running in MCP Studio mode")
            run_stdio_mode()
        elif mode == "--oauth":
            server_logger.info("🔐 Running in OAuth HTTP mode")
            run_oauth_mode()
        else:
            server_logger.error(f"❌ Invalid mode: {mode}")
            print("Usage: python server.py [--studio|--oauth]")
    else:
        # Default to stdio mode for Claude Desktop MCP integration
        server_logger.info("📡 Default mode: stdio (Claude Desktop)")
        print("📡 Starting Flight Booking MCP Server (stdio mode)...")
        print("🎯 Connected via MCP protocol")
        print("🏷️  Watermark: VG_FLIGHTMCP_2024")
        run_stdio_mode()

def main():
    """Main entry point for console script."""
    import sys
    
    server_logger.info("🎯 Flight Booking MCP Server - Main Entry Point")
    server_logger.info(f"   🏷️  Watermark: VG_FLIGHTMCP_2024")
    server_logger.info(f"   📋 Args: {sys.argv}")
    server_logger.info(f"   ⏰ Timestamp: {datetime.now().isoformat()}")
    
    if len(sys.argv) > 1 and sys.argv[1] == "--stdio":
        server_logger.info("📡 Mode: stdio transport (MCP over stdio)")
        # Run as MCP server over stdio
        mcp_server = MCPServer()
        mcp = mcp_server.create_stdio_server()
        mcp.run()
    else:
        server_logger.info("🌐 Mode: HTTP server (OAuth protected)")
        # Run as HTTP server
        server = MCPServer()
        app = server.create_oauth_server()
        
        config = server.config
        server_logger.info(f"🛫 Starting Flight Booking MCP Server")
        server_logger.info(f"   📍 URL: http://{config['host']}:{config['port']}")
        server_logger.info(f"   📚 Docs: http://{config['host']}:{config['port']}/docs")
        
        print(f"🛫 Starting Flight Booking MCP Server")
        print(f" on http://{config['host']}:{config['port']}")
        print(f"📚 API Documentation: http://{config['host']}:{config['port']}/docs")
        print(f"🔐 OAuth protected endpoints require Bearer token")
        
        uvicorn.run(
            app,
            host=config["host"],
            port=config["port"],
            log_level="info"
        )

if __name__ == "__main__":
    main()

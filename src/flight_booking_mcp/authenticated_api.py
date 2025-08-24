"""
Authenticated HTTP API Endpoints
Author: Vishal Gupta  
System: VG_FLIGHTMCP_2024

This provides OAuth-protected HTTP REST APIs alongside the MCP server.
These APIs require JWT token authentication, unlike MCP tools which work directly with Claude Desktop.
"""

from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
import logging
import uvicorn
from typing import Dict, Optional
from datetime import datetime

from .auth.token_validator import get_token_validator
from .services.flight_service import flight_service

# Configure logging
import os
log_dir = os.path.dirname(os.path.abspath(__file__))
api_log_file = os.path.join(log_dir, 'authenticated_api.log')

logging.basicConfig(
    level=logging.INFO,
    format='🔐 %(asctime)s - %(name)s - [%(levelname)s] - %(message)s',
    handlers=[
        logging.FileHandler(api_log_file),
        logging.StreamHandler()
    ]
)

api_logger = logging.getLogger("VG_Authenticated_API")

# Security scheme
security = HTTPBearer()

class AuthenticatedFlightAPI:
    """OAuth-protected Flight Booking REST API"""
    
    def __init__(self):
        self.app = FastAPI(
            title="VG Flight Booking API",
            description="OAuth 2.0 Protected Flight Booking API - VG_FLIGHTMCP_2024",
            version="1.0.0"
        )
        self.token_validator = get_token_validator()
        self.setup_routes()
    
    async def verify_token(self, credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
        """
        Verify JWT token and extract user information
        This is where OAuth authentication happens for HTTP APIs
        """
        token = credentials.credentials
        
        try:
            api_logger.info(f"🔍 Validating JWT token: {token[:20]}...")
            
            # Validate token using our token validator
            payload = self.token_validator.validate_token(token)
            
            api_logger.info(f"✅ Token valid for client: {payload.get('client_id')}")
            api_logger.info(f"   📋 Scope: {payload.get('scope')}")
            api_logger.info(f"   ⏰ Expires: {datetime.fromtimestamp(payload.get('exp', 0))}")
            
            return payload
            
        except jwt.ExpiredSignatureError:
            api_logger.error("❌ Token expired")
            raise HTTPException(
                status_code=401,
                detail="Token expired",
                headers={"WWW-Authenticate": "Bearer"}
            )
        except jwt.InvalidTokenError as e:
            api_logger.error(f"❌ Invalid token: {str(e)}")
            raise HTTPException(
                status_code=401,
                detail="Invalid authentication token",
                headers={"WWW-Authenticate": "Bearer"}
            )
        except Exception as e:
            api_logger.error(f"❌ Token validation error: {str(e)}")
            raise HTTPException(
                status_code=401,
                detail="Authentication failed",
                headers={"WWW-Authenticate": "Bearer"}
            )
    
    def log_api_access(self, request: Request, endpoint: str, user_info: dict):
        """Log authenticated API access"""
        client_ip = request.client.host if request.client else "unknown"
        client_id = user_info.get('client_id', 'unknown')
        
        api_logger.info(f"🌐 API Access: {endpoint}")
        api_logger.info(f"   👤 Client: {client_id}")
        api_logger.info(f"   🌍 IP: {client_ip}")
        api_logger.info(f"   🏷️  System: VG_FLIGHTMCP_2024")
    
    def setup_routes(self):
        """Setup OAuth-protected API routes"""
        
        @self.app.get("/")
        async def root():
            """API information endpoint"""
            return {
                "api": "VG Flight Booking API",
                "version": "1.0.0",
                "system": "VG_FLIGHTMCP_2024",
                "authentication": "OAuth 2.0 Required",
                "developer": "Vishal Gupta",
                "endpoints": {
                    "flights": "/api/flights/search",
                    "bookings": "/api/bookings",
                    "airports": "/api/airports"
                }
            }
        
        @self.app.get("/api/flights/search")
        async def search_flights(
            request: Request,
            origin: str,
            destination: str,
            date: str = "2024-12-01",
            user_info: dict = Depends(self.verify_token)
        ):
            """
            🔒 Search flights (OAuth Protected)
            Requires valid JWT token in Authorization header
            """
            self.log_api_access(request, "search_flights", user_info)
            
            try:
                # Call the flight service
                result = flight_service.search_flights(origin, destination, date)
                
                # Add authentication context
                result["_auth_info"] = {
                    "authenticated": True,
                    "client_id": user_info.get('client_id'),
                    "scope": user_info.get('scope'),
                    "system": "VG_FLIGHTMCP_2024"
                }
                
                api_logger.info(f"✅ Flight search successful: {len(result.get('flights', []))} flights found")
                return result
                
            except Exception as e:
                api_logger.error(f"❌ Flight search failed: {str(e)}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/api/bookings")
        async def create_booking(
            request: Request,
            booking_data: dict,
            user_info: dict = Depends(self.verify_token)
        ):
            """
            🔒 Create flight booking (OAuth Protected)
            Requires valid JWT token in Authorization header
            """
            self.log_api_access(request, "create_booking", user_info)
            
            try:
                flight_id = booking_data.get('flight_id')
                passenger_name = booking_data.get('passenger_name')
                email = booking_data.get('email')
                
                if not all([flight_id, passenger_name, email]):
                    raise HTTPException(
                        status_code=400,
                        detail="Missing required fields: flight_id, passenger_name, email"
                    )
                
                # Validate VG flight ID
                if not flight_id.startswith('VG'):
                    raise HTTPException(
                        status_code=400,
                        detail=f"Invalid flight ID format: {flight_id}. Must be VG-prefixed."
                    )
                
                result = flight_service.create_booking(flight_id, passenger_name, email)
                
                # Add authentication context
                result["_auth_info"] = {
                    "authenticated": True,
                    "client_id": user_info.get('client_id'),
                    "booking_authenticated_by": "VG_OAuth_System",
                    "system": "VG_FLIGHTMCP_2024"
                }
                
                api_logger.info(f"✅ Booking created: {result.get('booking_id')}")
                return result
                
            except HTTPException:
                raise
            except Exception as e:
                api_logger.error(f"❌ Booking creation failed: {str(e)}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/api/bookings")
        async def get_user_bookings(
            request: Request,
            email: str,
            user_info: dict = Depends(self.verify_token)
        ):
            """
            🔒 Get user bookings (OAuth Protected)
            Requires valid JWT token in Authorization header
            """
            self.log_api_access(request, "get_user_bookings", user_info)
            
            try:
                bookings = flight_service.get_bookings(email)
                
                result = {
                    "user_email": email,
                    "bookings": bookings,
                    "total_bookings": len(bookings),
                    "_auth_info": {
                        "authenticated": True,
                        "client_id": user_info.get('client_id'),
                        "data_access": "User bookings only",
                        "system": "VG_FLIGHTMCP_2024"
                    }
                }
                
                api_logger.info(f"✅ Retrieved {len(bookings)} bookings for {email}")
                return result
                
            except Exception as e:
                api_logger.error(f"❌ Failed to retrieve bookings: {str(e)}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/api/airports")
        async def get_airports(
            request: Request,
            user_info: dict = Depends(self.verify_token)
        ):
            """
            🔒 Get available airports (OAuth Protected)
            Requires valid JWT token in Authorization header
            """
            self.log_api_access(request, "get_airports", user_info)
            
            try:
                airports = flight_service.get_airports()
                
                result = {
                    "airports": airports,
                    "total_airports": len(airports),
                    "_auth_info": {
                        "authenticated": True,
                        "client_id": user_info.get('client_id'),
                        "data_source": "VG Airport Database",
                        "system": "VG_FLIGHTMCP_2024"
                    }
                }
                
                api_logger.info(f"✅ Retrieved {len(airports)} airports")
                return result
                
            except Exception as e:
                api_logger.error(f"❌ Failed to retrieve airports: {str(e)}")
                raise HTTPException(status_code=500, detail=str(e))


def create_authenticated_api() -> FastAPI:
    """Create the authenticated API app"""
    api_logger.info("🚀 Creating VG Authenticated Flight API")
    api_logger.info("🏷️  System: VG_FLIGHTMCP_2024")
    
    auth_api = AuthenticatedFlightAPI()
    
    api_logger.info("✅ Authenticated API created successfully")
    return auth_api.app


def run_authenticated_api_server(host: str = "localhost", port: int = 8001):
    """Run the authenticated API server"""
    app = create_authenticated_api()
    
    api_logger.info("🚀 Starting VG Authenticated Flight API Server")
    api_logger.info(f"🌐 Host: {host}:{port}")
    api_logger.info("🏷️  System: VG_FLIGHTMCP_2024")
    api_logger.info("🔐 All endpoints require OAuth 2.0 authentication")
    api_logger.info("-" * 60)
    
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    run_authenticated_api_server()

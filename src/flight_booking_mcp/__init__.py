"""
Flight Booking MCP Server
Author: Vishal Gupta
Created: August 2024
Watermark: VG_FLIGHTMCP_2024
License: Personal Project - All Rights Reserved
"""

__version__ = "1.0.0"
__author__ = "Vishal Gupta"
__watermark__ = "VG_FLIGHTMCP_2024"
__signature__ = "VG240824FLIGHT"
__created__ = "August 2024"

# Export project info
def get_project_info():
    """Returns project metadata information"""
    return {
        "author": __author__,
        "version": __version__,
        "system": __watermark__,
        "signature": __signature__,
        "created": __created__
    }

from .server import MCPServer
from .models import SearchFlightsRequest, CreateBookingRequest
from .services import FlightService, flight_service
from .auth import OAuthServer, TokenValidator

__version__ = "0.1.0"
__all__ = [
    "MCPServer",
    "SearchFlightsRequest", 
    "CreateBookingRequest",
    "FlightService",
    "flight_service",
    "OAuthServer",
    "TokenValidator"
]

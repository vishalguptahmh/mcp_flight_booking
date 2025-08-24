"""
MCP Tools Definitions
Clean separation of MCP tool definitions from business logic
"""

from fastmcp import FastMCP
from .services.flight_service import flight_service


def register_mcp_tools(mcp_server: FastMCP):
    """Register all MCP tools with the server"""
    
    @mcp_server.tool()
    def search_flights(origin: str, destination: str, date: str = "2024-12-01") -> dict:
        """Search for flights between two airports"""
        return flight_service.search_flights(origin, destination, date)
    
    @mcp_server.tool()
    def create_booking(flight_id: str, passenger_name: str, email: str = "passenger@example.com") -> dict:
        """Create a flight booking"""
        return flight_service.create_booking(flight_id, passenger_name, email)
    
    return mcp_server

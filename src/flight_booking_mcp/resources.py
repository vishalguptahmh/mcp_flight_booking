"""
MCP Resources Definitions
Author: Vishal Gupta
Created: August 2024
Watermark: VG_FLIGHTMCP_2024
Clean separation of MCP resource definitions from business logic
"""

import json
import os
from fastmcp import FastMCP
## Remove top-level import to avoid circular import


def load_airports_data():
    """Load airports data from JSON file"""
    try:
        # Get the path to the airports data file
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # The data folder is in the same directory as this file
        airports_file = os.path.join(current_dir, "data", "airports.json")
        
        with open(airports_file, 'r', encoding='utf-8') as f:
            return json.load(f)  # File is already in correct format
    except (FileNotFoundError, json.JSONDecodeError) as e:
        # Fallback to basic data if file is not found
        return {
            "airports": {
                "HYD": {"code": "HYD", "name": "Rajiv Gandhi International", "city": "Hyderabad", "country": "India"},
                "DEL": {"code": "DEL", "name": "Indira Gandhi International", "city": "Delhi", "country": "India"},
                "BOM": {"code": "BOM", "name": "Chhatrapati Shivaji Maharaj International", "city": "Mumbai", "country": "India"}
            },
            "metadata": {"total_airports": 3, "version": "fallback"}
        }


def register_mcp_resources(mcp_server: FastMCP):
    """Register all OAuth-protected MCP resources with the server"""
    
    @mcp_server.resource("file://airports")
    def get_airports():
        """
        Get comprehensive list of available airports with details
        🔐 REQUIRES OAUTH AUTHENTICATION
        """
        airports_data = load_airports_data()
        
        # Add OAuth security notice to header
        header = """
╔══════════════════════════════════════════════════════════╗
║              Flight Booking MCP v1.0                    ║
║              Developed by: Vishal Gupta                  ║
║              © August 2024 - All Rights Reserved        ║
║              System: VG_FLIGHTMCP_2024                  ║
║              🔐 OAuth Authentication Required            ║
╚══════════════════════════════════════════════════════════╝
"""
        
        # Format the data for easy reading
        formatted_output = header + "\n# Airport Information Database\n\n"
        
        for code, airport in airports_data["airports"].items():
            formatted_output += f"## {code} - {airport['name']}\n"
            formatted_output += f"**Location**: {airport['city']}, {airport['country']}\n"
            formatted_output += f"**Timezone**: {airport.get('timezone', 'N/A')}\n"
            
            if 'coordinates' in airport:
                coords = airport['coordinates']
                # Handle both 'lat'/'lng' and 'latitude'/'longitude' formats
                lat = coords.get('lat', coords.get('latitude', 'N/A'))
                lng = coords.get('lng', coords.get('longitude', 'N/A'))
                formatted_output += f"**Coordinates**: {lat}, {lng}\n"
            
            if 'facilities' in airport:
                formatted_output += f"**Facilities**: {', '.join(airport['facilities'])}\n"
            
            if 'airlines' in airport:
                formatted_output += f"**Airlines**: {', '.join(airport['airlines'])}\n"
            
            formatted_output += "\n---\n\n"
        
        # Add metadata with OAuth security info
        metadata = airports_data.get("metadata", {})
        formatted_output += f"**Total Airports**: {metadata.get('total_airports', len(airports_data['airports']))}\n"
        formatted_output += f"**Last Updated**: {metadata.get('last_updated', 'N/A')}\n"
        formatted_output += f"**Data Version**: {metadata.get('version', 'N/A')}\n"
        formatted_output += f"**Security Level**: OAuth Authentication Required\n"
        formatted_output += f"**Developer**: Vishal Gupta\n"
        formatted_output += f"**Watermark**: VG_FLIGHTMCP_2024\n"
        
        return formatted_output
    
    @mcp_server.prompt()
    def find_best_flight(budget: float, preferences: str = "economy") -> str:
        """
        Generate a prompt for finding the best flight within budget
        🔐 REQUIRES OAUTH AUTHENTICATION
        """
        return f"""Please help find the best flight within a ${budget} budget.
        
My preferences: {preferences}

Please consider:
- Price (must be under ${budget})
- Flight duration  
- Airline reputation
- Departure times
- Available amenities

Search for flights that match these criteria and provide recommendations.

🔐 NOTE: This service requires OAuth authentication and is developed by Vishal Gupta (VG_FLIGHTMCP_2024)"""
    
    @mcp_server.prompt()
    def handle_disruption(original_flight: str, reason: str) -> str:
        """
        Generate a prompt for handling flight disruptions
        🔐 REQUIRES OAUTH AUTHENTICATION
        """
        return f"""Flight {original_flight} has been disrupted due to: {reason}

Please help me:
1. Find alternative flights for the same route
2. Understand my rebooking options
3. Check compensation eligibility
4. Get contact information for customer service

What are my best options for resolving this disruption?

🔐 NOTE: This service requires OAuth authentication and is developed by Vishal Gupta (VG_FLIGHTMCP_2024)"""
    
    return mcp_server

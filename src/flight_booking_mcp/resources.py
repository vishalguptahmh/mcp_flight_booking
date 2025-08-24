"""
MCP Resources Definitions
Clean separation of MCP resource definitions from business logic
"""

import json
import os
from fastmcp import FastMCP
from .services.flight_service import flight_service


def load_airports_data():
    """Load airports data from JSON file"""
    try:
        # Get the path to the airports data file
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        airports_file = os.path.join(project_root, "data", "airports.json")
        
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
    """Register all MCP resources with the server"""
    
    print("[DEBUG] Registering MCP resource: file://airports")
    @mcp_server.resource("file://airports")
    def get_airports():
        """Get comprehensive list of available airports with details"""
        airports_data = load_airports_data()
        
        # Format the data for easy reading
        formatted_output = "# Airport Information Database\n\n"
        
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
        
        # Add metadata
        metadata = airports_data.get("metadata", {})
        formatted_output += f"**Total Airports**: {metadata.get('total_airports', 'N/A')}\n"
        formatted_output += f"**Last Updated**: {metadata.get('last_updated', 'N/A')}\n"
        formatted_output += f"**Data Version**: {metadata.get('version', 'N/A')}\n"
        
        return formatted_output
    
    print("[DEBUG] Registering MCP prompt: find_best_flight")
    @mcp_server.prompt()
    def find_best_flight(budget: float, preferences: str = "economy") -> str:
        """Generate a prompt for finding the best flight within budget"""
        return f"""Please help find the best flight within a ${budget} budget.
        
My preferences: {preferences}

Please consider:
- Price (must be under ${budget})
- Flight duration  
- Airline reputation
- Departure times
- Available amenities

Search for flights that match these criteria and provide recommendations."""
    
    print("[DEBUG] Registering MCP prompt: handle_disruption")
    @mcp_server.prompt()
    def handle_disruption(original_flight: str, reason: str) -> str:
        """Generate a prompt for handling flight disruptions"""
        return f"""Flight {original_flight} has been disrupted due to: {reason}

Please help me:
1. Find alternative flights for the same route
2. Understand my rebooking options
3. Check compensation eligibility
4. Get contact information for customer service

What are my best options for resolving this disruption?"""
    
    return mcp_server

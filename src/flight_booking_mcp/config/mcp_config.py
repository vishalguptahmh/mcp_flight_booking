"""
MCP Server Configuration
"""

import os

# MCP Server Settings
MCP_CONFIG = {
    "host": os.getenv("MCP_HOST", "localhost"),
    "port": int(os.getenv("MCP_PORT", "8000")),
    "server_name": "Flight Booking Server (OAuth Protected)",
    "version": "1.0.0",
}

# Flight Service Settings
FLIGHT_CONFIG = {
    "default_origin": "HYD",
    "default_destination": "DEL", 
    "default_price": 8000,
    "airlines": ["SkyConnect", "AirFlow", "Premium Airways"],
}

# Airport Data
AIRPORTS = {
    "HYD": {"name": "Rajiv Gandhi International", "city": "Hyderabad", "country": "India"},
    "DEL": {"name": "Indira Gandhi International", "city": "Delhi", "country": "India"},
    "LHR": {"name": "London Heathrow", "city": "London", "country": "UK"},
    "SFO": {"name": "San Francisco International", "city": "San Francisco", "country": "USA"},
    "ORD": {"name": "O'Hare International", "city": "Chicago", "country": "USA"},
    "DFW": {"name": "Dallas/Fort Worth International", "city": "Dallas", "country": "USA"},
    "CDG": {"name": "Charles de Gaulle", "city": "Paris", "country": "France"},
}

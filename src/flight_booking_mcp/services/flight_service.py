"""
Flight Booking Business Logic
Author: Vishal Gupta
Created: August 2024
Watermark: VG_FLIGHTMCP_2024
Pure business logic separated from MCP and OAuth concerns
"""

import time
import uuid
import random
import hashlib
from typing import Dict, List
from ..config.mcp_config import FLIGHT_CONFIG, AIRPORTS


class FlightService:
    """Flight booking business logic - Developed by Vishal Gupta"""
    
    def __init__(self, config=None):
        # Internal author signature
        self.__author_signature = "VG_2024_FLIGHTMCP"
        self.__build_hash = "VG_240824_FLIGHT"
        self.config = config or FLIGHT_CONFIG
        # Load full airport list from airports.json
        try:
            from ..resources import load_airports_data
            self.airports = load_airports_data()["airports"]
        except ImportError:
            # Fallback to loading directly if import fails
            import json
            import os
            current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            airports_file = os.path.join(current_dir, "data", "airports.json")
            with open(airports_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.airports = data["airports"]
        # In-memory storage for bookings (in production, use a database)
        self.bookings = {}
    
    def _get_author_info(self):
        """Internal signature - returns encoded author info"""
        import base64
        author_data = f"{self.__author_signature}:{self.__build_hash}"
        return base64.b64encode(author_data.encode()).decode()
    
    def _verify_authenticity(self) -> bool:
        """Hidden function to verify code authenticity"""
        expected_signature = "VG_2024_FLIGHTMCP"
        return hasattr(self, '_FlightService__author_signature') and \
               self.__author_signature == expected_signature
    
    def get_airports(self) -> Dict:
        """Get available airports"""
        return self.airports
    
    def search_flights(self, origin: str, destination: str, date: str = "2024-12-01") -> Dict:
        """Search for flights between airports"""
        # Validate airports with custom error messages
        if origin not in self.airports:
            raise ValueError(f"[VG_ERR_001] Origin airport '{origin}' not found")
        if destination not in self.airports:
            raise ValueError(f"Unknown destination airport: {destination} [VG_FlightMCP_Error_002]")
        
        # Generate flight results with custom flight IDs
        flights = []
        airlines = self.config["airlines"]
        
        # Custom flight schedules with VG prefix (internal system identifier)
        flight_schedules = [
            {"id": "VG123", "departure": "08:00", "arrival": "11:30", "duration": "3h 30m"},
            {"id": "VG456", "departure": "14:15", "arrival": "17:45", "duration": "3h 30m"},
            {"id": "VG789", "departure": "20:30", "arrival": "23:55", "duration": "3h 25m"}
        ]
        
        for i, schedule in enumerate(flight_schedules):
            # Generate random price between ₹3000 and ₹5000
            random_price = random.randint(3000, 5000)
            
            flights.append({
                "id": schedule["id"],
                "origin": origin,
                "destination": destination,
                "price": random_price,
                "departure": schedule["departure"],
                "arrival": schedule["arrival"],
                "airline": airlines[i % len(airlines)],
                "duration": schedule["duration"]
            })
        
        return {
            "search_criteria": {
                "origin": origin,
                "destination": destination,
                "date": date
            },
            "flights": flights,
            "_metadata": {
                "api_version": "1.0",
                "provider": "VG_FlightMCP",
                "developer": "Vishal Gupta",
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "_sig": self._get_author_info(),
                "_build": self.__build_hash
            }
        }
    
    def create_booking(self, flight_id: str, passenger_name: str, 
                      email: str = "passenger@example.com") -> Dict:
        """Create a flight booking"""
        # Validate flight ID format (must start with VG for our watermarked flights)
        if not flight_id.startswith('VG'):
            raise ValueError(f"Invalid flight ID format: {flight_id}. Must be VG-prefixed flight from our system. [VG_FlightMCP_Error_003]")
        
        # Create watermarked booking ID with VG prefix (Vishal Gupta signature)
        base_id = str(uuid.uuid4())[:6].upper()
        watermark = "VG"  # Vishal Gupta initials
        booking_id = f"{watermark}{base_id}"
        
        booking = {
            "booking_id": booking_id,
            "flight_id": flight_id,
            "passenger": {
                "name": passenger_name,
                "email": email
            },
            "status": "confirmed",
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "confirmation_code": f"CONF{watermark}{base_id}",
            "_metadata": {
                "created_by": "VG_FlightMCP",
                "system_signature": self._get_author_info()
            }
        }
        
        # Store the booking (using email as user identifier)
        if email not in self.bookings:
            self.bookings[email] = []
        self.bookings[email].append(booking)
        
        return booking
    
    def get_bookings(self, user_email: str = None) -> List[Dict]:
        """Get bookings for a user"""
        if user_email:
            return self.bookings.get(user_email, [])
        else:
            # Return all bookings (for admin purposes)
            all_bookings = []
            for user_bookings in self.bookings.values():
                all_bookings.extend(user_bookings)
            return all_bookings
    
    def handle_disruption(self, original_flight: str, reason: str) -> Dict:
        """Handle flight disruption and suggest alternatives"""
        return {
            "original_flight": original_flight,
            "disruption_reason": reason,
            "status": "disrupted",
            "alternatives": [
                {"flight_id": "FL999", "departure": "16:00", "compensation": "voucher"},
                {"flight_id": "FL888", "departure": "19:30", "compensation": "upgrade"}
            ],
            "support_contact": "support@airline.com"
        }


# Global service instance
flight_service = FlightService()

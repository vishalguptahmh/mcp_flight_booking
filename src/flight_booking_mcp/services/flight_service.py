"""
Flight Booking Business Logic
Pure business logic separated from MCP and OAuth concerns
"""

import time
import uuid
from typing import Dict, List
from ..config.mcp_config import FLIGHT_CONFIG, AIRPORTS


class FlightService:
    """Flight booking business logic"""
    
    def __init__(self, config=None):
        self.config = config or FLIGHT_CONFIG
        self.airports = AIRPORTS
        # In-memory storage for bookings (in production, use a database)
        self.bookings = {}
    
    def get_airports(self) -> Dict:
        """Get available airports"""
        return self.airports
    
    def search_flights(self, origin: str, destination: str, date: str = "2024-12-01") -> Dict:
        """Search for flights between airports"""
        # Validate airports
        if origin not in self.airports:
            raise ValueError(f"Unknown origin airport: {origin}")
        if destination not in self.airports:
            raise ValueError(f"Unknown destination airport: {destination}")
        
        # Generate flight results
        flights = []
        base_price = self.config["default_price"]
        airlines = self.config["airlines"]
        
        flight_schedules = [
            {"id": "FL123", "departure": "08:00", "arrival": "11:30", "duration": "3h 30m"},
            {"id": "FL456", "departure": "14:15", "arrival": "17:45", "duration": "3h 30m"},
            {"id": "FL789", "departure": "20:30", "arrival": "23:55", "duration": "3h 25m"}
        ]
        
        for i, schedule in enumerate(flight_schedules):
            flights.append({
                "id": schedule["id"],
                "origin": origin,
                "destination": destination,
                "price": base_price,
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
            "flights": flights
        }
    
    def create_booking(self, flight_id: str, passenger_name: str, 
                      email: str = "passenger@example.com") -> Dict:
        """Create a flight booking"""
        booking_id = str(uuid.uuid4())[:8].upper()
        
        booking = {
            "booking_id": booking_id,
            "flight_id": flight_id,
            "passenger": {
                "name": passenger_name,
                "email": email
            },
            "status": "confirmed",
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "confirmation_code": f"CONF{booking_id}"
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

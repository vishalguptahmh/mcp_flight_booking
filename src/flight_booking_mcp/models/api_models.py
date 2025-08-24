"""
Pydantic models for API requests
"""
from pydantic import BaseModel
from typing import Optional

class SearchFlightsRequest(BaseModel):
    """Request model for flight search"""
    origin: str
    destination: str
    date: str = "2024-12-01"

class CreateBookingRequest(BaseModel):
    """Request model for creating booking"""
    flight_id: str
    passenger_name: str
    email: str = "passenger@example.com"

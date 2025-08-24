"""Request and response models for flight booking MCP server."""

from pydantic import BaseModel
from typing import Optional

class SearchFlightsRequest(BaseModel):
    """Request model for searching flights."""
    origin: str
    destination: str
    date: str

class CreateBookingRequest(BaseModel):
    """Request model for creating a booking."""
    flight_id: str
    passenger_name: str
    email: str

__all__ = ["SearchFlightsRequest", "CreateBookingRequest"]

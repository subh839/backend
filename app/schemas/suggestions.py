from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum
from datetime import datetime

class SuggestionType(str, Enum):
    ROUTE_OPTIMIZATION = "route_optimization"
    CHARGE_SCHEDULE = "charge_schedule"
    STATION_SELECTION = "station_selection"
    DRIVING_TIPS = "driving_tips"
    BATTERY_HEALTH = "battery_health"

class Suggestion(BaseModel):
    type: SuggestionType
    title: str
    description: str
    priority: int = Field(ge=1, le=5, description="Priority from 1 (highest) to 5 (lowest)")
    estimated_savings: Optional[float] = None
    action_items: List[str] = []
    estimated_time_minutes: Optional[int] = None

class RangeCalculation(BaseModel):
    current_location: List[float] = Field(..., description="[latitude, longitude]")
    current_battery_percentage: float
    max_distance_km: float
    reachable_radius_km: float
    reachable_area_sqkm: float
    usable_battery_kwh: float
    estimated_range_with_full_charge_km: float
    safe_range_km: float = Field(..., description="80% of max range for safety buffer")

class StationInfo(BaseModel):
    station_id: str
    name: str
    latitude: float
    longitude: float
    distance_km: float
    connector_types: List[str]
    available_ports: int
    total_ports: int
    pricing_per_kwh: Optional[float] = None
    estimated_wait_time_minutes: Optional[int] = None
    rating: Optional[float] = Field(None, ge=0, le=5)

class OptimalRoute(BaseModel):
    total_distance_km: float
    total_time_minutes: float
    total_energy_kwh: float
    charging_stops: List[Dict[str, Any]]
    waypoints: List[List[float]]

class Summary(BaseModel):
    total_suggestions: int
    high_priority_count: int
    estimated_total_savings: Optional[float] = None
    next_action: str
    confidence_score: float = Field(..., ge=0, le=1)
    generated_at: datetime = Field(default_factory=datetime.now)
    version: str = "1.0"

class SuggestionsResponse(BaseModel):
    suggestions: List[Suggestion]
    range_info: Optional[RangeCalculation] = None
    optimal_route: Optional[OptimalRoute] = None
    nearby_stations: Optional[List[StationInfo]] = None
    summary: Summary
    
    class Config:
        json_schema_extra = {
            "example": {
                "suggestions": [
                    {
                        "type": "station_selection",
                        "title": "Charge at Supercharger Station",
                        "description": "Recommended charging station within your range",
                        "priority": 1,
                        "estimated_savings": 5.25,
                        "action_items": ["Navigate to station", "Plug in charger"]
                    }
                ],
                "range_info": {
                    "current_location": [40.7128, -74.0060],
                    "current_battery_percentage": 65.5,
                    "max_distance_km": 250.0,
                    "reachable_radius_km": 200.0,
                    "reachable_area_sqkm": 125600.0,
                    "usable_battery_kwh": 45.0,
                    "estimated_range_with_full_charge_km": 380.0,
                    "safe_range_km": 200.0
                },
                "optimal_route": {
                    "total_distance_km": 185.5,
                    "total_time_minutes": 145.0,
                    "total_energy_kwh": 32.5,
                    "charging_stops": [],
                    "waypoints": [[40.7128, -74.0060], [40.7580, -73.9855]]
                },
                "nearby_stations": [
                    {
                        "station_id": "station_123",
                        "name": "EVgo Charging Station",
                        "latitude": 40.7130,
                        "longitude": -74.0062,
                        "distance_km": 0.5,
                        "connector_types": ["CCS", "CHAdeMO"],
                        "available_ports": 2,
                        "total_ports": 4,
                        "pricing_per_kwh": 0.35
                    }
                ],
                "summary": {
                    "total_suggestions": 3,
                    "high_priority_count": 1,
                    "estimated_total_savings": 15.75,
                    "next_action": "Navigate to nearest charging station",
                    "confidence_score": 0.85,
                    "generated_at": "2024-01-15T10:30:00Z",
                    "version": "1.0"
                }
            }
        }
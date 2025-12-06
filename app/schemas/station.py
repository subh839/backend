# In app/schemas/station.py
from pydantic import BaseModel, ConfigDict, Field, field_validator
from typing import Optional, List
from datetime import datetime
from bson import ObjectId

class StationBase(BaseModel):
    name: str
    address: str
    city: str
    state: str
    latitude: float
    longitude: float
    power_kw: float
    cost_per_kwh: float
    charger_type: str  # ✅ Changed from connector_type to charger_type (matches MongoDB)
    available_chargers: int
    total_chargers: int
    is_operational: bool = True
    # Add optional fields that exist in your MongoDB
    is_24_7: Optional[bool] = False
    amenities: Optional[List[str]] = []
    rating: Optional[float] = None
    operator: Optional[str] = None
    station_id: Optional[str] = None

class StationCreate(StationBase):
    zip_code: str  # For creation, expect string

class Station(StationBase):
    id: str = Field(alias="_id")
    zip_code: str  # Changed to string
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    @field_validator("zip_code", mode="before")
    @classmethod
    def convert_zip_code_to_string(cls, v):
        """Convert zip_code to string if it's numeric"""
        if v is None:
            return ""
        # Convert to string (handles int, float, etc.)
        return str(int(v)) if isinstance(v, (int, float)) else str(v)
    
    @field_validator("id", mode="before")
    @classmethod
    def convert_objectid_to_string(cls, v):
        """Convert ObjectId to string"""
        if isinstance(v, ObjectId):
            return str(v)
        return v
    
    # Add validator to handle missing connector_type by using charger_type
    @field_validator("charger_type", mode="before")
    @classmethod
    def ensure_charger_type(cls, v, info):
        """Ensure charger_type exists, use connector_type if it doesn't"""
        # If charger_type is missing but connector_type exists, use it
        if v is None and "connector_type" in info.data:
            return info.data["connector_type"]
        return v
    
    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True
    )

class NearbyStation(Station):
    distance_km: float
    time_to_reach_minutes: float
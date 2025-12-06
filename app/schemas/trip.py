# In app/schemas/trip.py
from pydantic import BaseModel, ConfigDict, Field, field_validator
from typing import Optional
from datetime import datetime, timedelta
from bson import ObjectId

class TripBase(BaseModel):
    start_latitude: float
    start_longitude: float
    end_latitude: float
    end_longitude: float
    start_address: str
    end_address: str
    car_id: str
    distance_km: float
    estimated_energy_kwh: float
    actual_energy_kwh: float
    duration_minutes: int
    start_time: datetime
    charging_stops: int = 0
    total_charging_time_minutes: int = 0
    cost_usd: float = 0.0
    weather: Optional[str] = None

class TripCreate(TripBase):
    pass

class Trip(TripBase):
    # Use 'id' field with alias to map from '_id'
    id: str = Field(alias="_id")
    user_id: str
    end_time: Optional[datetime] = None
    notes: Optional[str] = None
    created_at: datetime
    
    # Field validator to handle ObjectId conversion
    @field_validator("id", mode="before")
    @classmethod
    def validate_id(cls, v):
        """Convert ObjectId to string if needed"""
        if isinstance(v, ObjectId):
            return str(v)
        return v
    
    # Field validator to calculate end_time
    @field_validator("end_time", mode="before")
    @classmethod
    def calculate_end_time(cls, v, info):
        """Calculate end_time from start_time and duration"""
        if v is None:
            # Get the data from context
            data = info.data if hasattr(info, 'data') else {}
            
            start_time = data.get("start_time")
            duration = data.get("duration_minutes", 0)
            
            if isinstance(start_time, datetime) and duration:
                # Calculate end_time = start_time + duration
                return start_time + timedelta(minutes=duration)
        return v
    
    # Make sure the model can populate by alias
    model_config = ConfigDict(
        populate_by_name=True,  # This allows using both 'id' and '_id'
        from_attributes=True
    )
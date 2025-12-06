from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from enum import Enum
from datetime import datetime
from bson import ObjectId

class CarType(str, Enum):
    SEDAN = "sedan"
    SUV = "suv"
    TRUCK = "truck"
    HATCHBACK = "hatchback"
    CROSSOVER = "crossover"

class CarBase(BaseModel):
    make: str
    model: str
    year: int
    license_plate: str
    battery_capacity_kwh: float
    efficiency_kwh_per_km: float
    car_type: CarType = CarType.SUV

class CarCreate(CarBase):
    current_battery_percentage: float = 100.0
    color: Optional[str] = None
    vin: Optional[str] = None

class CarUpdate(BaseModel):
    current_battery_percentage: Optional[float] = None
    efficiency_kwh_per_km: Optional[float] = None

# FIXED: Updated Car model to match MongoDB structure
class Car(CarBase):
    # Choose ONE of these ID fields, not both:
    
    # OPTION A: Use 'car_id' (maps to MongoDB '_id')
    car_id: str = Field(alias="_id")
    
    # OPTION B: Use 'id' (maps to MongoDB '_id') - pick this if you want consistency with User model
    # id: str = Field(alias="_id")
    
    user_id: str
    current_battery_percentage: float = 100.0
    color: Optional[str] = None
    vin: Optional[str] = None
    created_at: datetime  # Changed from str to datetime!
    
    model_config = ConfigDict(
        populate_by_name=True,  # Allows using alias
        from_attributes=True
    )
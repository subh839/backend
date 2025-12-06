from app.database import mongodb
from bson import ObjectId
from datetime import datetime
from typing import Optional, Dict, Any

async def create_car(car_data: dict, user_id: str) -> str:
    """Create a new car for a user"""
    db = mongodb.get_database()
    
    # Add user_id and timestamps
    car_data["user_id"] = user_id
    car_data["created_at"] = datetime.utcnow()
    
    # Validate and set default efficiency if not provided or invalid
    if "efficiency_kwh_per_km" not in car_data or float(car_data.get("efficiency_kwh_per_km", 0)) <= 0:
        car_data["efficiency_kwh_per_km"] = 0.2  # Default reasonable efficiency
    
    # Validate battery capacity
    if "battery_capacity_kwh" not in car_data or float(car_data.get("battery_capacity_kwh", 0)) <= 0:
        car_data["battery_capacity_kwh"] = 50.0  # Default reasonable capacity
    
    # Validate battery percentage
    if "current_battery_percentage" not in car_data:
        car_data["current_battery_percentage"] = 100.0
    
    # Insert into database
    result = await db.cars.insert_one(car_data)
    return str(result.inserted_id)

async def get_user_cars(user_id: str) -> list:
    """Get all cars for a user"""
    db = mongodb.get_database()
    cars = await db.cars.find({"user_id": user_id}).to_list(length=100)
    
    # ❌ REMOVE THIS - Don't add duplicate id field
    # for car in cars:
    #     car["id"] = str(car["_id"])
    
    return cars

async def get_car_by_id(car_id: str) -> Optional[Dict[str, Any]]:
    """Get a car by ID with validation"""
    db = mongodb.get_database()
    
    try:
        obj_id = ObjectId(car_id)
    except:
        return None
    
    car = await db.cars.find_one({"_id": obj_id})
    
    if car:
        # Convert to dict
        car_dict = dict(car)
        
        # ✅ Validate and fix efficiency if needed
        if "efficiency_kwh_per_km" in car_dict:
            try:
                eff = float(car_dict["efficiency_kwh_per_km"])
                if eff <= 0:
                    car_dict["efficiency_kwh_per_km"] = 0.2  # Set default
            except (ValueError, TypeError):
                car_dict["efficiency_kwh_per_km"] = 0.2  # Set default
        
        # ✅ Validate battery capacity
        if "battery_capacity_kwh" in car_dict:
            try:
                cap = float(car_dict["battery_capacity_kwh"])
                if cap <= 0:
                    car_dict["battery_capacity_kwh"] = 50.0  # Set default
            except (ValueError, TypeError):
                car_dict["battery_capacity_kwh"] = 50.0  # Set default
        
        # ✅ Validate battery percentage
        if "current_battery_percentage" in car_dict:
            try:
                bat = float(car_dict["current_battery_percentage"])
                if bat < 0:
                    car_dict["current_battery_percentage"] = 0
                elif bat > 100:
                    car_dict["current_battery_percentage"] = 100
            except (ValueError, TypeError):
                car_dict["current_battery_percentage"] = 50.0  # Set default
        
        # ❌ DON'T add duplicate id field
        # car_dict["id"] = str(car_dict["_id"])
        
        return car_dict
    
    return None

async def update_car_battery(car_id: str, battery_percentage: float) -> bool:
    """Update car battery percentage"""
    db = mongodb.get_database()
    
    try:
        obj_id = ObjectId(car_id)
    except:
        return False
    
    # Validate battery percentage
    if battery_percentage < 0:
        battery_percentage = 0
    elif battery_percentage > 100:
        battery_percentage = 100
    
    result = await db.cars.update_one(
        {"_id": obj_id},
        {"$set": {"current_battery_percentage": battery_percentage}}
    )
    
    return result.modified_count > 0

async def update_car(car_id: str, update_data: Dict[str, Any]) -> bool:
    """Update car information"""
    db = mongodb.get_database()
    
    try:
        obj_id = ObjectId(car_id)
    except:
        return False
    
    # Remove _id and id fields from update data
    update_data.pop("_id", None)
    update_data.pop("id", None)
    
    # Validate efficiency if being updated
    if "efficiency_kwh_per_km" in update_data:
        eff = float(update_data["efficiency_kwh_per_km"])
        if eff <= 0:
            update_data["efficiency_kwh_per_km"] = 0.2
    
    # Add updated timestamp
    update_data["updated_at"] = datetime.utcnow()
    
    result = await db.cars.update_one(
        {"_id": obj_id},
        {"$set": update_data}
    )
    
    return result.modified_count > 0

async def delete_car(car_id: str) -> bool:
    """Delete a car"""
    db = mongodb.get_database()
    
    try:
        obj_id = ObjectId(car_id)
    except:
        return False
    
    result = await db.cars.delete_one({"_id": obj_id})
    return result.deleted_count > 0
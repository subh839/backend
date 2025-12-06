# In app/routers/suggestions.py
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional, Dict
from bson import ObjectId
from datetime import datetime
import json

from app.auth import get_current_user
from app.crud.car import get_car_by_id
from app.utils.calculations import calculate_range_from_point, calculate_distance
from app.crud.station import get_stations_near_location

router = APIRouter(prefix="/suggestions", tags=["suggestions"])

def convert_mongo_document(doc):
    """Convert MongoDB document with ObjectId to JSON-serializable dict"""
    if doc is None:
        return None
    
    if isinstance(doc, ObjectId):
        return str(doc)
    
    if isinstance(doc, datetime):
        return doc.isoformat()
    
    if isinstance(doc, dict):
        result = {}
        for key, value in doc.items():
            if key == '_id' and isinstance(value, ObjectId):
                result['id'] = str(value)
                result['_id'] = str(value)
            elif isinstance(value, ObjectId):
                result[key] = str(value)
            elif isinstance(value, datetime):
                result[key] = value.isoformat()
            elif isinstance(value, dict):
                result[key] = convert_mongo_document(value)
            elif isinstance(value, list):
                result[key] = [convert_mongo_document(item) if isinstance(item, (dict, ObjectId)) else item for item in value]
            else:
                result[key] = value
        return result
    
    if isinstance(doc, list):
        return [convert_mongo_document(item) for item in doc]
    
    return doc

@router.get("/range-calculation")
async def calculate_travel_range(
    latitude: float = Query(..., description="Current latitude"),
    longitude: float = Query(..., description="Current longitude"),
    car_id: str = Query(..., description="Car ID"),
    battery_percentage: Optional[float] = Query(None, description="Current battery percentage"),
    terrain_factor: float = Query(1.0, description="Terrain factor (1.0=flat, 1.2=hilly)"),
    weather_factor: float = Query(1.0, description="Weather factor (1.0=ideal, 1.15=cold/rain)"),
    current_user: dict = Depends(get_current_user)
):
    """Calculate travel range from current location"""
    # Convert user_id from ObjectId to string
    user_id = str(current_user.get("_id") or current_user.get("id"))
    
    # Get car details and convert MongoDB document
    car_doc = await get_car_by_id(car_id)
    if not car_doc:
        raise HTTPException(status_code=404, detail="Car not found")
    
    car = convert_mongo_document(car_doc)
    
    # Check car ownership
    car_user_id = str(car.get("user_id", ""))
    if car_user_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to access this car")
    
    # Extract car data with validation
    battery_capacity = float(car.get("battery_capacity_kwh", 0))
    efficiency = float(car.get("efficiency_kwh_per_km", 0))
    current_battery = float(battery_percentage or car.get("current_battery_percentage", 100))
    
    # Validate efficiency and set default if invalid
    if efficiency <= 0:
        efficiency = 0.2  # Default reasonable efficiency
    
    # Validate battery capacity
    if battery_capacity <= 0:
        battery_capacity = 50.0  # Default reasonable capacity
    
    # Validate battery percentage
    if current_battery < 0:
        current_battery = 0
    elif current_battery > 100:
        current_battery = 100
    
    # Validate factors
    if terrain_factor <= 0:
        terrain_factor = 1.0
    
    if weather_factor <= 0:
        weather_factor = 1.0
    
    # Calculate current battery in kWh
    current_battery_kwh = battery_capacity * (current_battery / 100)
    
    # Calculate range using the utility function
    try:
        range_info = calculate_range_from_point(
            current_location=(latitude, longitude),
            current_battery_kwh=current_battery_kwh,
            efficiency_kwh_per_km=efficiency,
            battery_capacity_kwh=battery_capacity,
            min_safety_battery=10.0,
            terrain_factor=terrain_factor,
            weather_factor=weather_factor
        )
    except ZeroDivisionError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot calculate range: {str(e)}. Check car efficiency values."
        )
    
    # Get nearby charging stations within safe range
    safe_range = range_info.get("max_distance_km", 0) * 0.8  # 80% of max range
    
    # Get all stations (without distance filter)
    all_stations_docs = await get_stations_near_location(
        latitude=latitude,
        longitude=longitude
    )
    
    # Process stations to add distance information
    processed_stations = []
    if all_stations_docs:
        for station_doc in all_stations_docs:
            # Convert MongoDB document
            station = convert_mongo_document(station_doc)
            
            # Calculate distance to this station
            station_lat = station.get("latitude", 0)
            station_lon = station.get("longitude", 0)
            distance = calculate_distance(latitude, longitude, station_lat, station_lon)
            
            # Only include stations within safe range
            if distance <= safe_range:
                station["distance_km"] = round(distance, 2)
                station["time_to_reach_minutes"] = round(distance * 1.5, 1)
                
                # Calculate if this station is reachable with current battery
                energy_to_station = distance * efficiency
                station["reachable_with_current_battery"] = energy_to_station <= current_battery_kwh
                
                processed_stations.append(station)
        
        # Sort by distance
        processed_stations.sort(key=lambda x: x["distance_km"])
    
    # Calculate full charge range with safety check
    full_charge_range_km = 0.0
    if efficiency > 0:
        full_charge_range_km = round(battery_capacity / efficiency, 2)
    
    # Build response - ensure all IDs are strings
    response = {
        "starting_point": {
            "latitude": latitude,
            "longitude": longitude
        },
        "car_info": {
            "car_id": str(car_id),  # Ensure string
            "battery_capacity_kwh": battery_capacity,
            "efficiency_kwh_per_km": efficiency,
            "current_battery_percentage": current_battery,
            "current_battery_kwh": round(current_battery_kwh, 2),
            "full_charge_range_km": full_charge_range_km
        },
        "range_analysis": range_info,
        "terrain_and_weather": {
            "terrain_factor": terrain_factor,
            "weather_factor": weather_factor,
            "effective_efficiency": round(efficiency * terrain_factor * weather_factor, 3)
        },
        "nearby_charging_stations": {
            "count": len(processed_stations),
            "within_safe_range_km": safe_range,
            "stations": processed_stations[:5]  # Top 5 closest
        },
        "recommendations": []
    }
    
    # Add recommendations based on battery level
    if current_battery < 20:
        response["recommendations"].append("⚡ Charge immediately - Battery critically low")
        response["recommendations"].append(f"🔋 Current range: {range_info.get('max_distance_km', 0)} km")
        if processed_stations:
            closest = processed_stations[0]
            response["recommendations"].append(f"📍 Nearest station: {closest.get('name', 'Unknown')} ({closest['distance_km']} km away)")
    elif current_battery < 50:
        response["recommendations"].append("🔋 Consider charging soon for optimal range")
        response["recommendations"].append(f"📏 Safe range: {range_info.get('max_distance_km', 0) * 0.8:.1f} km")
    else:
        response["recommendations"].append("✅ Battery level sufficient")
        response["recommendations"].append(f"🗺️ Maximum range: {range_info.get('max_distance_km', 0):.1f} km")
    
    # Add efficiency warning if efficiency is very low
    if efficiency < 0.1:
        response["recommendations"].append("⚠️ Car efficiency seems unusually low. Please verify car settings.")
    
    return response
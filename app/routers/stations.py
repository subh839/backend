from fastapi import APIRouter, Depends, Query
from bson import ObjectId
from app.schemas.station import Station, NearbyStation
from app.crud.station import get_stations_near_location, get_all_stations
from app.auth import get_current_user
from typing import List, Optional

router = APIRouter(prefix="/stations", tags=["charging_stations"])

@router.get("/nearby", response_model=List[NearbyStation])
async def get_nearby_stations(
    latitude: float = Query(..., description="Current latitude"),
    longitude: float = Query(..., description="Current longitude"),
    max_distance: float = Query(50, description="Maximum distance in km"),
    current_user: dict = Depends(get_current_user)
):
    """Find charging stations near location"""
    stations = await get_stations_near_location(latitude, longitude, max_distance)
    
    from app.utils.calculations import calculate_distance
    
    processed_stations = []
    for station in stations:
        # Convert to dict if needed
        if not isinstance(station, dict):
            station = dict(station)
        
        # ✅ Ensure charger_type field exists (map from connector_type if needed)
        if "charger_type" not in station and "connector_type" in station:
            station["charger_type"] = station["connector_type"]
        
        # ✅ Convert zip_code to string
        if "zip_code" in station:
            station["zip_code"] = str(station["zip_code"])
        
        # ✅ Convert ObjectId to string
        if "_id" in station:
            station["_id"] = str(station["_id"])
        
        # ✅ Remove duplicate id field
        if "id" in station:
            del station["id"]
        
        # Calculate distance
        station_lat = station.get("latitude", 0)
        station_lon = station.get("longitude", 0)
        distance = calculate_distance(latitude, longitude, station_lat, station_lon)
        
        # Add distance fields
        station["distance_km"] = round(distance, 2)
        station["time_to_reach_minutes"] = round(distance * 1.5, 1)
        
        processed_stations.append(station)
    
    return processed_stations

@router.get("/", response_model=List[Station])
async def list_stations(
    skip: int = Query(0, description="Number of records to skip"),
    limit: int = Query(100, description="Maximum number of records to return"),
    current_user: Optional[dict] = Depends(get_current_user)
):
    """Get all stations (can be public or protected)"""
    stations = await get_all_stations(skip, limit)
    
    processed_stations = []
    for station in stations:
        # Convert to dict if needed
        if not isinstance(station, dict):
            station = dict(station)
        
        # ✅ Ensure charger_type field exists
        if "charger_type" not in station and "connector_type" in station:
            station["charger_type"] = station["connector_type"]
        
        # ✅ Convert zip_code to string
        if "zip_code" in station:
            station["zip_code"] = str(station["zip_code"])
        
        # ✅ Convert ObjectId to string
        if "_id" in station:
            station["_id"] = str(station["_id"])
        
        # ✅ Remove duplicate id field
        if "id" in station:
            del station["id"]
        
        # ✅ Add default values for optional fields
        if "is_24_7" not in station:
            station["is_24_7"] = False
        if "amenities" not in station:
            station["amenities"] = []
        if "rating" not in station:
            station["rating"] = 0.0
        if "operator" not in station:
            station["operator"] = ""
        if "station_id" not in station:
            station["station_id"] = ""
        
        processed_stations.append(station)
    
    return processed_stations
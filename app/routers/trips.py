# In app/routers/trips.py
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from datetime import datetime, timedelta
from bson import ObjectId
from app.schemas.trip import Trip, TripCreate
from app.crud.trip import create_trip, get_user_trips, get_trip_stats, get_trip_by_id
from app.auth import get_current_user

router = APIRouter(prefix="/trips", tags=["trips"])

@router.get("/history", response_model=List[Trip])
async def get_trip_history(
    skip: int = Query(0, description="Number of records to skip"),
    limit: int = Query(50, description="Maximum number of records to return"),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    car_id: Optional[str] = Query(None, description="Filter by car ID"),
    current_user: dict = Depends(get_current_user)
):
    """Get trip history for the current user"""
    user_id = str(current_user.get("_id") or current_user.get("id"))
    
    # Build query filters
    filters = {}
    if car_id:
        filters["car_id"] = car_id
    
    if start_date or end_date:
        filters["start_time"] = {}
        if start_date:
            try:
                start_datetime = datetime.fromisoformat(start_date + "T00:00:00")
                filters["start_time"]["$gte"] = start_datetime
            except:
                raise HTTPException(status_code=400, detail="Invalid start date format")
        
        if end_date:
            try:
                end_datetime = datetime.fromisoformat(end_date + "T23:59:59")
                filters["start_time"]["$lte"] = end_datetime
            except:
                raise HTTPException(status_code=400, detail="Invalid end date format")
    
    trips = await get_user_trips(user_id, skip=skip, limit=limit, **filters)
    
    # Prepare trips for Pydantic model
    processed_trips = []
    for trip in trips:
        # Convert to dict if needed
        if not isinstance(trip, dict):
            trip = dict(trip)
        
        # ✅ Ensure we have both '_id' and 'id' for alias mapping
        # The Pydantic model expects 'id' but has alias='_id'
        # So we should keep '_id' and let Pydantic map it
        if "_id" in trip:
            # Convert ObjectId to string if needed
            if isinstance(trip["_id"], ObjectId):
                trip["_id"] = str(trip["_id"])
        else:
            # If no '_id', try to use 'id'
            if "id" in trip:
                trip["_id"] = trip["id"]
        
        # ✅ Calculate end_time if not present
        if "end_time" not in trip:
            start_time = trip.get("start_time")
            duration = trip.get("duration_minutes", 0)
            if isinstance(start_time, datetime) and duration:
                trip["end_time"] = start_time + timedelta(minutes=duration)
        
        # ✅ Ensure notes field exists
        if "notes" not in trip:
            trip["notes"] = None
        
        # ✅ Ensure weather field exists
        if "weather" not in trip:
            trip["weather"] = None
        
        processed_trips.append(trip)
    
    return processed_trips

@router.post("/", response_model=Trip)
async def save_trip(
    trip_data: TripCreate, 
    current_user: dict = Depends(get_current_user)
):
    """Save a new trip"""
    user_id = str(current_user.get("_id") or current_user.get("id"))
    
    # Convert Pydantic model to dict
    trip_dict = trip_data.dict()
    trip_dict["user_id"] = user_id
    
    # Calculate end_time if not provided
    if "end_time" not in trip_dict:
        start_time = trip_dict.get("start_time")
        duration = trip_dict.get("duration_minutes", 0)
        if start_time and duration:
            trip_dict["end_time"] = start_time + timedelta(minutes=duration)
    
    # Ensure notes field exists
    if "notes" not in trip_dict:
        trip_dict["notes"] = None
    
    # Create trip
    trip_id = await create_trip(trip_dict)
    
    # Fetch and return the created trip
    created_trip = await get_trip_by_id(trip_id)
    
    if not created_trip:
        raise HTTPException(status_code=500, detail="Failed to retrieve created trip")
    
    # Process the trip document
    created_trip = dict(created_trip)
    
    # Ensure proper ID field mapping
    if "_id" in created_trip:
        if isinstance(created_trip["_id"], ObjectId):
            created_trip["_id"] = str(created_trip["_id"])
    
    # Ensure all required fields exist
    if "end_time" not in created_trip:
        created_trip["end_time"] = None
    if "notes" not in created_trip:
        created_trip["notes"] = None
    if "weather" not in created_trip:
        created_trip["weather"] = None
    
    return created_trip

@router.get("/stats")
async def get_trip_statistics(current_user: dict = Depends(get_current_user)):
    """Get trip statistics"""
    user_id = str(current_user.get("_id") or current_user.get("id"))
    
    stats = await get_trip_stats(user_id)
    
    if not stats:
        return {
            "total_trips": 0,
            "total_distance": 0,
            "total_energy": 0,
            "total_cost": 0,
            "total_charging_time": 0,
            "average_distance": 0
        }
    
    # Remove MongoDB _id field
    if "_id" in stats:
        del stats["_id"]
    
    return stats
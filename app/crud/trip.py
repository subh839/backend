# app/crud/trip.py
from app.database import mongodb
from bson import ObjectId
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List

async def create_trip(trip_data: dict) -> str:
    """
    Create a new trip in the database
    
    Args:
        trip_data: Dictionary containing trip information
    
    Returns:
        String representation of the inserted document ID
    """
    db = mongodb.get_database()
    
    # Add timestamps
    trip_data["created_at"] = datetime.utcnow()
    
    # Insert the trip
    result = await db.trips.insert_one(trip_data)
    
    # Return the ID as string
    return str(result.inserted_id)

async def get_user_trips(
    user_id: str, 
    skip: int = 0, 
    limit: int = 50, 
    **filters
) -> List[Dict[str, Any]]:
    """
    Get trips for a specific user with optional filters
    
    Args:
        user_id: ID of the user
        skip: Number of records to skip (for pagination)
        limit: Maximum number of records to return
        **filters: Additional filter criteria
    
    Returns:
        List of trip documents
    """
    db = mongodb.get_database()
    
    # Build the query
    query = {"user_id": user_id}
    
    # Add any additional filters
    if filters:
        query.update(filters)
    
    # Fetch trips from database
    trips = await db.trips.find(query)\
        .sort("created_at", -1)\
        .skip(skip)\
        .limit(limit)\
        .to_list(length=limit)
    
    return trips

async def get_trip_stats(user_id: str) -> Optional[Dict[str, Any]]:
    """
    Get trip statistics for a user
    
    Args:
        user_id: ID of the user
    
    Returns:
        Dictionary with trip statistics or None if no trips
    """
    db = mongodb.get_database()
    
    pipeline = [
        {"$match": {"user_id": user_id}},
        {"$group": {
            "_id": None,
            "total_trips": {"$sum": 1},
            "total_distance": {"$sum": "$distance_km"},
            "total_energy": {"$sum": "$actual_energy_kwh"},
            "total_cost": {"$sum": "$cost_usd"},
            "total_charging_time": {"$sum": "$total_charging_time_minutes"},
            "average_distance": {"$avg": "$distance_km"}
        }}
    ]
    
    result = await db.trips.aggregate(pipeline).to_list(length=1)
    
    return result[0] if result else None

async def get_trip_by_id(trip_id: str) -> Optional[Dict[str, Any]]:
    """
    Get a trip by its ID
    
    Args:
        trip_id: ID of the trip
    
    Returns:
        Trip document or None if not found
    """
    db = mongodb.get_database()
    
    try:
        # Convert string ID to ObjectId
        obj_id = ObjectId(trip_id)
    except:
        # Invalid ID format
        return None
    
    # Find the trip
    trip = await db.trips.find_one({"_id": obj_id})
    
    return trip

async def get_recent_trips(user_id: str, days: int = 30) -> List[Dict[str, Any]]:
    """
    Get recent trips for a user within the last N days
    
    Args:
        user_id: ID of the user
        days: Number of days to look back
    
    Returns:
        List of recent trip documents
    """
    db = mongodb.get_database()
    
    # Calculate cutoff date
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    # Query for recent trips
    trips = await db.trips.find({
        "user_id": user_id,
        "created_at": {"$gte": cutoff_date}
    }).sort("created_at", -1).to_list(None)
    
    return trips

async def delete_trip(trip_id: str) -> bool:
    """
    Delete a trip by ID
    
    Args:
        trip_id: ID of the trip to delete
    
    Returns:
        True if deleted, False otherwise
    """
    db = mongodb.get_database()
    
    try:
        obj_id = ObjectId(trip_id)
    except:
        return False
    
    result = await db.trips.delete_one({"_id": obj_id})
    
    return result.deleted_count > 0

async def update_trip(trip_id: str, update_data: Dict[str, Any]) -> bool:
    """
    Update a trip
    
    Args:
        trip_id: ID of the trip to update
        update_data: Dictionary of fields to update
    
    Returns:
        True if updated, False otherwise
    """
    db = mongodb.get_database()
    
    try:
        obj_id = ObjectId(trip_id)
    except:
        return False
    
    # Remove _id from update data if present
    update_data.pop('_id', None)
    update_data.pop('id', None)
    
    # Add updated timestamp
    update_data["updated_at"] = datetime.utcnow()
    
    result = await db.trips.update_one(
        {"_id": obj_id},
        {"$set": update_data}
    )
    
    return result.modified_count > 0

# Export all functions
__all__ = [
    'create_trip',
    'get_user_trips',
    'get_trip_stats',
    'get_trip_by_id',
    'get_recent_trips',
    'delete_trip',
    'update_trip'
]
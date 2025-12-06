from fastapi import APIRouter, Depends, HTTPException, status
from bson import ObjectId
from app.schemas.car import CarCreate, CarUpdate, Car
from app.crud.car import create_car, get_user_cars, update_car_battery, get_car_by_id
from app.auth import get_current_user
from typing import List
from datetime import datetime

router = APIRouter(prefix="/cars", tags=["cars"])

@router.post("/", response_model=Car)  # Changed from dict to Car
async def add_car(car: CarCreate, current_user: dict = Depends(get_current_user)):
    """Add a new car for the current user"""
    car_data = car.dict()
    
    # Get user ID (converting from string or ObjectId)
    user_id = str(current_user.get("_id") or current_user.get("id"))
    
    car_id = await create_car(car_data, user_id)
    
    # Fetch the created car
    created_car = await get_car_by_id(car_id)
    
    # Prepare car for response
    if created_car:
        # Convert ObjectId to string and remove duplicate id field
        car_dict = dict(created_car)
        
        if "_id" in car_dict and isinstance(car_dict["_id"], ObjectId):
            car_dict["_id"] = str(car_dict["_id"])
        
        if "id" in car_dict:
            del car_dict["id"]
        
        return car_dict
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve created car"
        )

@router.get("/", response_model=List[Car])
async def get_cars(current_user: dict = Depends(get_current_user)):
    """Get all cars for the current user"""
    # Get user ID
    user_id = str(current_user.get("_id") or current_user.get("id"))
    
    cars = await get_user_cars(user_id)
    
    # Process each car for response
    result = []
    for car in cars:
        car_dict = dict(car)
        
        # Convert ObjectId to string
        if "_id" in car_dict and isinstance(car_dict["_id"], ObjectId):
            car_dict["_id"] = str(car_dict["_id"])
        
        # Remove duplicate 'id' field if it exists
        if "id" in car_dict:
            del car_dict["id"]
        
        # Ensure created_at is datetime (not string)
        if "created_at" in car_dict and isinstance(car_dict["created_at"], str):
            try:
                car_dict["created_at"] = datetime.fromisoformat(car_dict["created_at"].replace('Z', '+00:00'))
            except:
                car_dict["created_at"] = datetime.utcnow()
        
        result.append(car_dict)
    
    return result

@router.get("/{car_id}", response_model=Car)
async def get_car(car_id: str, current_user: dict = Depends(get_current_user)):
    """Get a specific car"""
    # Get user ID
    user_id = str(current_user.get("_id") or current_user.get("id"))
    
    # Validate car_id format
    try:
        ObjectId(car_id)
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid car ID format"
        )
    
    car = await get_car_by_id(car_id)
    
    if not car:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Car not found"
        )
    
    # Check ownership
    car_user_id = str(car.get("user_id"))
    if car_user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this car"
        )
    
    # Prepare car for response
    car_dict = dict(car)
    
    # Convert ObjectId to string
    if "_id" in car_dict and isinstance(car_dict["_id"], ObjectId):
        car_dict["_id"] = str(car_dict["_id"])
    
    # Remove duplicate 'id' field
    if "id" in car_dict:
        del car_dict["id"]
    
    # Ensure created_at is datetime
    if "created_at" in car_dict and isinstance(car_dict["created_at"], str):
        try:
            car_dict["created_at"] = datetime.fromisoformat(car_dict["created_at"].replace('Z', '+00:00'))
        except:
            car_dict["created_at"] = datetime.utcnow()
    
    return car_dict

@router.put("/{car_id}/battery", response_model=dict)
async def update_battery(
    car_id: str, 
    update_data: CarUpdate, 
    current_user: dict = Depends(get_current_user)
):
    """Update car battery percentage"""
    # Get user ID
    user_id = str(current_user.get("_id") or current_user.get("id"))
    
    # Validate car_id format
    try:
        ObjectId(car_id)
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid car ID format"
        )
    
    car = await get_car_by_id(car_id)
    
    if not car:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Car not found"
        )
    
    # Check ownership
    car_user_id = str(car.get("user_id"))
    if car_user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this car"
        )
    
    # Update battery
    if update_data.current_battery_percentage is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Battery percentage is required"
        )
    
    await update_car_battery(car_id, update_data.current_battery_percentage)
    
    return {"message": "Battery updated successfully"}
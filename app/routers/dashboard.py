from fastapi import APIRouter, Depends, HTTPException
from app.auth import get_current_user
from app.crud.trip import get_user_trips, get_trip_stats
from app.crud.car import get_user_cars
from app.crud.station import get_all_stations
from datetime import datetime, timedelta
import math

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

@router.get("/stats")
async def get_dashboard_stats(current_user: dict = Depends(get_current_user)):
    """Dashboard statistics"""
    
    # Get user ID safely
    user_id = str(current_user.get("_id") or current_user.get("id"))
    
    # Get user's trips
    trips = await get_user_trips(user_id, limit=1000)
    
    # Get user's cars
    cars = await get_user_cars(user_id)
    
    # Get trip statistics
    trip_stats = await get_trip_stats(user_id)
    
    # Calculate recent trips (last 30 days)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    recent_trips = []
    for trip in trips:
        start_time = trip.get("start_time")
        if isinstance(start_time, datetime) and start_time > thirty_days_ago:
            recent_trips.append(trip)
    
    # Calculate car statistics
    car_stats = []
    for car in cars:
        # Convert car to dict if needed
        if not isinstance(car, dict):
            car = dict(car)
        
        # Get car ID safely
        car_id = str(car.get("_id") or car.get("id"))
        
        # Filter trips for this car
        car_trips = []
        for trip in trips:
            trip_car_id = str(trip.get("car_id", ""))
            if trip_car_id == car_id:
                car_trips.append(trip)
        
        # Calculate efficiency if there are trips
        total_distance = 0.0
        total_energy = 0.0
        
        for trip in car_trips:
            total_distance += float(trip.get("distance_km", 0))
            total_energy += float(trip.get("actual_energy_kwh", 0))
        
        # Get car efficiency values with defaults
        car_efficiency = float(car.get("efficiency_kwh_per_km", 0))
        battery_capacity = float(car.get("battery_capacity_kwh", 0))
        current_battery = float(car.get("current_battery_percentage", 0))
        
        # Calculate average efficiency
        if total_distance > 0:
            avg_efficiency = total_energy / total_distance
        else:
            # Use car's efficiency if no trips, but ensure it's not zero
            avg_efficiency = car_efficiency if car_efficiency > 0 else 0.2  # Default to 0.2 kWh/km
        
        # Ensure avg_efficiency is not zero for range calculation
        if avg_efficiency <= 0:
            avg_efficiency = 0.2  # Default reasonable efficiency
        
        # Calculate estimated range with safety check
        estimated_range = 0.0
        if avg_efficiency > 0 and battery_capacity > 0 and current_battery > 0:
            estimated_range = round(
                (battery_capacity * current_battery / 100) / avg_efficiency, 
                2
            )
        
        # Determine battery health
        battery_health = "Good"
        if current_battery < 20:
            battery_health = "Critical"
        elif current_battery < 50:
            battery_health = "Low"
        
        car_stats.append({
            "car_id": car_id,
            "car_name": f"{car.get('make', 'Unknown')} {car.get('model', 'Unknown')}",
            "year": car.get("year", 0),
            "license_plate": car.get("license_plate", ""),
            "current_battery_percentage": current_battery,
            "total_trips": len(car_trips),
            "total_distance_km": round(total_distance, 2),
            "average_efficiency_kwh_per_km": round(avg_efficiency, 3),
            "battery_health": battery_health,
            "estimated_range_km": estimated_range
        })
    
    # Get charging stations summary
    all_stations = await get_all_stations(limit=500)
    
    # Count fast chargers and available chargers safely
    fast_chargers = 0
    available_chargers = 0
    total_cost = 0.0
    
    for station in all_stations:
        if not isinstance(station, dict):
            station = dict(station)
        
        power_kw = float(station.get("power_kw", 0))
        if power_kw >= 100:
            fast_chargers += 1
        
        available_chargers += int(station.get("available_chargers", 0))
        total_cost += float(station.get("cost_per_kwh", 0))
    
    # Calculate carbon savings (approximate)
    if trip_stats and isinstance(trip_stats, dict):
        total_energy_kwh = float(trip_stats.get("total_energy", 0))
        total_distance_km = float(trip_stats.get("total_distance", 0))
    else:
        total_energy_kwh = 0.0
        total_distance_km = 0.0
    
    # Calculate environmental impact
    gas_car_emissions_kg = total_distance_km * 0.08 * 2.3  # Liters * emissions per liter
    ev_emissions_kg = total_energy_kwh * 0.4  # kWh * emissions per kWh
    carbon_saved_kg = max(0, gas_car_emissions_kg - ev_emissions_kg)
    
    # Generate insights
    insights = []
    
    if cars:
        # Get first car safely
        first_car = cars[0]
        if not isinstance(first_car, dict):
            first_car = dict(first_car)
        
        battery_percent = float(first_car.get("current_battery_percentage", 100))
        car_make = first_car.get("make", "Your car")
        
        if battery_percent < 30:
            insights.append({
                "type": "warning",
                "title": "Low Battery",
                "message": f"Your {car_make} has {battery_percent}% battery.",
                "action": "Consider charging soon for optimal range."
            })
    
    if recent_trips:
        insights.append({
            "type": "success",
            "title": "Active User",
            "message": f"You've taken {len(recent_trips)} trips in the last 30 days.",
            "action": "Keep up the eco-friendly travel!"
        })
    
    # Calculate average cost per kWh safely
    avg_cost_per_kwh = 0.0
    if all_stations:
        avg_cost_per_kwh = round(total_cost / len(all_stations), 3)
    
    # Prepare response
    return {
        "user": {
            "username": current_user.get("username", ""),
            "email": current_user.get("email", ""),
            "full_name": current_user.get("full_name", ""),
            "member_since": (
                current_user.get("created_at").strftime("%Y-%m-%d") 
                if isinstance(current_user.get("created_at"), datetime) 
                else "N/A"
            )
        },
        "summary": {
            "total_trips": trip_stats.get("total_trips", 0) if isinstance(trip_stats, dict) else 0,
            "total_distance_km": round(float(trip_stats.get("total_distance", 0)), 2) if isinstance(trip_stats, dict) else 0,
            "total_energy_kwh": round(float(trip_stats.get("total_energy", 0)), 2) if isinstance(trip_stats, dict) else 0,
            "total_cost_usd": round(float(trip_stats.get("total_cost", 0)), 2) if isinstance(trip_stats, dict) else 0,
            "average_trip_distance_km": round(float(trip_stats.get("average_distance", 0)), 2) if isinstance(trip_stats, dict) else 0,
            "recent_trips_30_days": len(recent_trips),
            "total_charging_time_hours": round(
                (float(trip_stats.get("total_charging_time", 0)) if isinstance(trip_stats, dict) else 0) / 60, 
                1
            )
        },
        "environmental_impact": {
            "carbon_saved_kg": round(carbon_saved_kg, 2),
            "money_saved_usd": round(total_distance_km * 0.08 * 1.2 - total_energy_kwh * 0.12, 2),
            "equivalent_trees": round(carbon_saved_kg / 21.77, 1) if carbon_saved_kg > 0 else 0,
            "gasoline_saved_liters": round(total_distance_km * 0.08, 1)
        },
        "cars": car_stats,
        "charging_network": {
            "total_stations": len(all_stations),
            "fast_chargers": fast_chargers,
            "available_chargers_now": available_chargers,
            "average_cost_per_kwh": avg_cost_per_kwh
        },
        "insights": insights
    }
from haversine import haversine
from typing import List, Tuple, Dict, Optional
import math

def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance between two points in kilometers using haversine formula"""
    return haversine((lat1, lon1), (lat2, lon2))

def calculate_energy_required(distance_km: float, efficiency_kwh_per_km: float) -> float:
    """Calculate energy required for a distance"""
    if efficiency_kwh_per_km <= 0:
        efficiency_kwh_per_km = 0.2  # Default reasonable efficiency
    
    return distance_km * efficiency_kwh_per_km

def can_reach_destination(current_battery_kwh: float, required_energy_kwh: float, safety_margin: float = 0.1) -> bool:
    """Check if destination can be reached with current battery"""
    return current_battery_kwh >= required_energy_kwh * (1 + safety_margin)

def calculate_range_from_point(
    current_location: Tuple[float, float],
    current_battery_kwh: float,
    efficiency_kwh_per_km: float,
    battery_capacity_kwh: float,
    min_safety_battery: float = 10.0,
    terrain_factor: float = 1.0,
    weather_factor: float = 1.0
) -> Dict:
    """
    Calculate travel range from current point
    
    Args:
        current_location: (latitude, longitude) tuple
        current_battery_kwh: Current battery capacity in kWh
        efficiency_kwh_per_km: Car efficiency in kWh per km
        battery_capacity_kwh: Maximum battery capacity in kWh
        min_safety_battery: Minimum safety battery percentage
        terrain_factor: Multiplier for terrain difficulty
        weather_factor: Multiplier for weather conditions
    
    Returns:
        Dictionary with range information
    """
    # Validate inputs
    if efficiency_kwh_per_km <= 0:
        efficiency_kwh_per_km = 0.2  # Default reasonable efficiency
    
    if battery_capacity_kwh <= 0:
        battery_capacity_kwh = 50.0  # Default reasonable capacity
    
    if current_battery_kwh < 0:
        current_battery_kwh = 0
    elif current_battery_kwh > battery_capacity_kwh:
        current_battery_kwh = battery_capacity_kwh
    
    if terrain_factor <= 0:
        terrain_factor = 1.0
    
    if weather_factor <= 0:
        weather_factor = 1.0
    
    # Calculate effective efficiency with safety check
    effective_efficiency = efficiency_kwh_per_km * terrain_factor * weather_factor
    
    # Ensure effective_efficiency is not zero
    if effective_efficiency <= 0:
        effective_efficiency = 0.2  # Minimum reasonable efficiency
    
    # Calculate usable battery (accounting for safety margin)
    min_safety_kwh = battery_capacity_kwh * (min_safety_battery / 100)
    usable_battery_kwh = max(0, current_battery_kwh - min_safety_kwh)
    
    # Calculate distances with safety check
    max_distance_km = 0.0
    estimated_range_with_full_charge_km = 0.0
    
    if effective_efficiency > 0:
        max_distance_km = usable_battery_kwh / effective_efficiency
        estimated_range_with_full_charge_km = battery_capacity_kwh / effective_efficiency
    
    reachable_radius_km = max_distance_km
    reachable_area_sqkm = math.pi * (reachable_radius_km ** 2) if max_distance_km > 0 else 0
    
    # Determine range status
    if max_distance_km < 20:
        range_status = "Critical"
        suggestion = "Charge immediately"
    elif max_distance_km < 50:
        range_status = "Low"
        suggestion = "Plan to charge soon"
    elif max_distance_km < 100:
        range_status = "Moderate"
        suggestion = "Monitor battery level"
    else:
        range_status = "Good"
        suggestion = "Continue driving"
    
    return {
        "max_distance_km": round(max_distance_km, 2),
        "reachable_radius_km": round(reachable_radius_km, 2),
        "reachable_area_sqkm": round(reachable_area_sqkm, 2),
        "usable_battery_kwh": round(usable_battery_kwh, 2),
        "estimated_range_with_full_charge_km": round(estimated_range_with_full_charge_km, 2),
        "range_status": range_status,
        "suggestion": suggestion,
        "conditions": {
            "terrain_factor": terrain_factor,
            "weather_factor": weather_factor,
            "min_safety_battery_percent": min_safety_battery,
            "effective_efficiency_kwh_per_km": round(effective_efficiency, 3)
        }
    }

def find_nearest_stations(current_location: Tuple[float, float], stations: List[dict], max_distance_km: float = 50) -> List[dict]:
    """Find nearest charging stations"""
    nearby_stations = []
    
    for station in stations:
        # Calculate distance to station
        distance = calculate_distance(
            current_location[0], current_location[1],
            station.get("latitude", 0), station.get("longitude", 0)
        )
        
        # Check if station is within range and has available chargers
        if distance <= max_distance_km and station.get("available_chargers", 0) > 0:
            station_with_distance = station.copy()
            station_with_distance["distance_km"] = round(distance, 2)
            station_with_distance["time_to_reach_minutes"] = round(distance * 1.5, 1)
            
            # Calculate estimated charge time if power_kw is available
            if station_with_distance.get("power_kw") and station_with_distance["power_kw"] > 0:
                # Assuming 20 kWh needed for typical charge
                charge_time = 20 / station_with_distance["power_kw"] * 60
                station_with_distance["estimated_charge_time_minutes"] = round(charge_time, 1)
            else:
                station_with_distance["estimated_charge_time_minutes"] = 45.0  # Default
            
            nearby_stations.append(station_with_distance)
    
    # Sort by distance and return top 10
    nearby_stations.sort(key=lambda x: x["distance_km"])
    return nearby_stations[:10]

def calculate_route_with_charging(
    start_location: Tuple[float, float],
    end_location: Tuple[float, float],
    current_battery_kwh: float,
    efficiency_kwh_per_km: float,
    battery_capacity_kwh: float,
    stations: List[dict],
    min_safety_battery: float = 10.0
) -> Dict:
    """Calculate route with charging stops if needed"""
    # Calculate total distance
    total_distance = calculate_distance(
        start_location[0], start_location[1],
        end_location[0], end_location[1]
    )
    
    # Calculate required energy
    required_energy = calculate_energy_required(total_distance, efficiency_kwh_per_km)
    
    # Check if can reach directly
    if can_reach_destination(current_battery_kwh, required_energy):
        return {
            "can_reach_directly": True,
            "total_distance_km": round(total_distance, 2),
            "required_energy_kwh": round(required_energy, 2),
            "charging_stops": [],
            "message": "Can reach destination directly"
        }
    
    # Find charging stations along the route
    # This is a simplified version - you might want to implement more sophisticated routing
    midpoint = (
        (start_location[0] + end_location[0]) / 2,
        (start_location[1] + end_location[1]) / 2
    )
    
    nearby_stations = find_nearest_stations(midpoint, stations, max_distance_km=50)
    
    if nearby_stations:
        return {
            "can_reach_directly": False,
            "total_distance_km": round(total_distance, 2),
            "required_energy_kwh": round(required_energy, 2),
            "charging_stops_needed": True,
            "suggested_stations": nearby_stations[:3],  # Top 3 closest stations
            "message": "Need to charge at a station along the route"
        }
    
    return {
        "can_reach_directly": False,
        "total_distance_km": round(total_distance, 2),
        "required_energy_kwh": round(required_energy, 2),
        "charging_stops_needed": True,
        "suggested_stations": [],
        "message": "No charging stations found along route"
    }
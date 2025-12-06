from app.database import mongodb
from bson import ObjectId

async def create_station(station_data: dict):
    db = mongodb.get_database()
    station_data["location"] = {
        "type": "Point",
        "coordinates": [station_data["longitude"], station_data["latitude"]]
    }
    result = await db.charging_stations.insert_one(station_data)
    return str(result.inserted_id)

async def get_stations_near_location(latitude: float, longitude: float, max_distance_km: float = 50):
    db = mongodb.get_database()
    max_distance_meters = max_distance_km * 1000
    
    stations = await db.charging_stations.find({
        "location": {
            "$near": {
                "$geometry": {
                    "type": "Point",
                    "coordinates": [longitude, latitude]
                },
                "$maxDistance": max_distance_meters
            }
        }
    }).to_list(length=20)
    
    for station in stations:
        station["id"] = str(station["_id"])
    return stations

async def get_all_stations(skip: int = 0, limit: int = 100):
    db = mongodb.get_database()
    stations = await db.charging_stations.find().skip(skip).limit(limit).to_list(length=limit)
    for station in stations:
        station["id"] = str(station["_id"])
    return stations
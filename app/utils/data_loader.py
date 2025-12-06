import pandas as pd
import json
from datetime import datetime
from app.database import get_sync_client
from app.auth import get_password_hash
import warnings

def load_csv_to_mongodb():
    db = get_sync_client()
    
    print("📊 Starting data loading process...")
    
    # Load Users - WITH PASSWORD LENGTH FIX
    print("1. Loading users...")
    try:
        users_df = pd.read_csv("data/users.csv")
        users_data = []
        
        for _, row in users_df.iterrows():
            try:
                # Get password and ensure it's a string
                password = str(row["password"])
                
                # FIX: Truncate password if it's too long for bcrypt (72 bytes limit)
                # Note: We're using SHA256 now, but still handle long passwords
                if len(password.encode('utf-8')) > 100:  # Reasonable limit
                    print(f"   ⚠️  Truncating long password for user {row['email']}")
                    # Truncate but keep it meaningful
                    password = password[:50] + "..."
                
                # FIX: Handle special characters that might cause issues
                # Clean the password string
                password = password.strip()
                
                user_data = {
                    "user_id": row["user_id"],
                    "email": row["email"],
                    "username": row["username"],
                    "hashed_password": get_password_hash(password),
                    "full_name": row["full_name"],
                    "phone": row["phone"],
                    "created_at": datetime.fromisoformat(row["created_at"]) if pd.notna(row["created_at"]) else datetime.utcnow(),
                    "is_active": True,
                    "role": "user"
                }
                users_data.append(user_data)
                
            except Exception as user_error:
                print(f"   ⚠️  Skipping user {row.get('email', 'unknown')}: {str(user_error)}")
                # Create user with default password
                try:
                    default_user = {
                        "user_id": row["user_id"],
                        "email": row["email"],
                        "username": row["username"],
                        "hashed_password": get_password_hash("default123"),  # Default password
                        "full_name": row["full_name"],
                        "phone": row["phone"],
                        "created_at": datetime.utcnow(),
                        "is_active": True,
                        "role": "user"
                    }
                    users_data.append(default_user)
                    print(f"   ✅ Created user {row['email']} with default password")
                except:
                    continue
        
        db.users.delete_many({})
        if users_data:
            db.users.insert_many(users_data)
            print(f"   ✅ Loaded {len(users_data)} users")
            
            # Show sample of loaded users
            print(f"   📋 Sample users loaded:")
            for i in range(min(3, len(users_data))):
                print(f"      - {users_data[i]['email']}")
            
    except Exception as e:
        print(f"   ❌ Error loading users: {e}")
        import traceback
        traceback.print_exc()
    
    # Load Cars (unchanged)
    print("2. Loading cars...")
    try:
        cars_df = pd.read_csv("data/cars.csv")
        cars_data = []
        
        for _, row in cars_df.iterrows():
            car_data = {
                "car_id": row["car_id"],
                "user_id": row["user_id"],
                "make": row["make"],
                "model": row["model"],
                "year": int(row["year"]),
                "license_plate": row["license_plate"],
                "battery_capacity_kwh": float(row["battery_capacity_kwh"]),
                "efficiency_kwh_per_km": float(row["efficiency_kwh_per_km"]),
                "current_battery_percentage": float(row["current_battery_percentage"]),
                "car_type": row["car_type"],
                "vin": row["vin"],
                "color": row["color"],
                "created_at": datetime.fromisoformat(row["created_at"]) if pd.notna(row["created_at"]) else datetime.utcnow()
            }
            cars_data.append(car_data)
        
        db.cars.delete_many({})
        if cars_data:
            db.cars.insert_many(cars_data)
            print(f"   ✅ Loaded {len(cars_data)} cars")
    except Exception as e:
        print(f"   ❌ Error loading cars: {e}")
    
    # Load Stations (unchanged)
    print("3. Loading charging stations...")
    try:
        stations_df = pd.read_csv("data/charging_stations.csv")
        stations_data = []
        
        for _, row in stations_df.iterrows():
            try:
                amenities = json.loads(row["amenities"]) if pd.notna(row["amenities"]) else []
            except:
                amenities = []
            
            station_data = {
                "station_id": row["station_id"],
                "name": row["name"],
                "address": row["address"],
                "city": row["city"],
                "state": row["state"],
                "zip_code": row["zip_code"],
                "latitude": float(row["latitude"]),
                "longitude": float(row["longitude"]),
                "location": {
                    "type": "Point",
                    "coordinates": [float(row["longitude"]), float(row["latitude"])]
                },
                "charger_type": row["charger_type"],
                "operator": row["operator"],
                "available_chargers": int(row["available_chargers"]),
                "total_chargers": int(row["total_chargers"]),
                "power_kw": float(row["power_kw"]),
                "cost_per_kwh": float(row["cost_per_kwh"]),
                "is_24_7": bool(row["is_24_7"]) if pd.notna(row["is_24_7"]) else True,
                "amenities": amenities,
                "rating": float(row["rating"]) if pd.notna(row["rating"]) else 4.0,
                "created_at": datetime.fromisoformat(row["created_at"]) if pd.notna(row["created_at"]) else datetime.utcnow()
            }
            stations_data.append(station_data)
        
        db.charging_stations.delete_many({})
        if stations_data:
            db.charging_stations.insert_many(stations_data)
            print(f"   ✅ Loaded {len(stations_data)} charging stations")
    except Exception as e:
        print(f"   ❌ Error loading stations: {e}")
    
    # Load Trips (unchanged)
    print("4. Loading trips...")
    try:
        trips_df = pd.read_csv("data/trips.csv")
        trips_data = []
        
        for _, row in trips_df.iterrows():
            trip_data = {
                "trip_id": row["trip_id"],
                "user_id": row["user_id"],
                "car_id": row["car_id"],
                "start_latitude": float(row["start_latitude"]),
                "start_longitude": float(row["start_longitude"]),
                "end_latitude": float(row["end_latitude"]),
                "end_longitude": float(row["end_longitude"]),
                "start_address": row["start_address"],
                "end_address": row["end_address"],
                "distance_km": float(row["distance_km"]),
                "estimated_energy_kwh": float(row["estimated_energy_kwh"]),
                "actual_energy_kwh": float(row["actual_energy_kwh"]),
                "duration_minutes": int(row["duration_minutes"]),
                "start_time": datetime.fromisoformat(row["start_time"]) if pd.notna(row["start_time"]) else datetime.utcnow(),
                "end_time": datetime.fromisoformat(row["end_time"]) if pd.notna(row["end_time"]) else None,
                "charging_stops": int(row["charging_stops"]),
                "total_charging_time_minutes": int(row["total_charging_time_minutes"]),
                "cost_usd": float(row["cost_usd"]),
                "weather": row["weather"],
                "notes": row["notes"],
                "created_at": datetime.utcnow()
            }
            trips_data.append(trip_data)
        
        db.trips.delete_many({})
        if trips_data:
            db.trips.insert_many(trips_data)
            print(f"   ✅ Loaded {len(trips_data)} trips")
    except Exception as e:
        print(f"   ❌ Error loading trips: {e}")
    
    print("🎉 Data loading completed!")
    
    # Print summary
    print(f"\n📈 Database Summary:")
    print(f"   Users: {db.users.count_documents({})}")
    print(f"   Cars: {db.cars.count_documents({})}")
    print(f"   Charging Stations: {db.charging_stations.count_documents({})}")
    print(f"   Trips: {db.trips.count_documents({})}")
    
    # Show some sample users for testing
    print(f"\n🔑 Sample users for testing (password: 'pass123'):")
    sample_users = list(db.users.find({}).limit(5))
    for user in sample_users:
        print(f"   - {user['email']}")

if __name__ == "__main__":
    # Suppress bcrypt warnings if any
    warnings.filterwarnings("ignore", message=".*bcrypt.*")
    load_csv_to_mongodb()
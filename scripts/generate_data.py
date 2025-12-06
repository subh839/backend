import csv
import random
from datetime import datetime, timedelta
import json
import os

def ensure_directory(filepath):
    """Ensure the directory for the given file path exists."""
    directory = os.path.dirname(filepath)
    if not os.path.exists(directory):
        os.makedirs(directory)

def generate_users_csv(filename="data/users.csv"):
    """Generate 60 users"""
    users = []
    
    # Create 60 users
    for i in range(1, 61):
        users.append({
            "user_id": f"user_{i:03d}",
            "email": f"user{i}@example.com",
            "username": f"user_{i:03d}",
            "password": "password123",
            "full_name": f"User {i} Name",
            "phone": f"+1-555-{random.randint(100,999)}-{random.randint(1000,9999)}",
            "created_at": datetime.now().isoformat()
        })
    
    # Write to CSV
    with open(filename, 'w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=users[0].keys())
        writer.writeheader()
        writer.writerows(users)
    
    print(f"✅ Generated {len(users)} users in {filename}")

def generate_users_csv(filename="data/users.csv"):
    """Generate 60 users with shorter passwords"""
    ensure_directory(filename)
    users = []
    
    # Create 60 users with SHORTER passwords (bcrypt limit is 72 bytes)
    for i in range(1, 61):
        users.append({
            "user_id": f"user_{i:03d}",
            "email": f"user{i}@example.com",
            "username": f"user_{i:03d}",
            "password": "pass123",  # Shorter password (bcrypt has 72 byte limit)
            "full_name": f"User {i} Name",
            "phone": f"+1-555-{random.randint(100,999)}-{random.randint(1000,9999)}",
            "created_at": datetime.now().isoformat()
        })
    
    # Write to CSV
    with open(filename, 'w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=users[0].keys())
        writer.writeheader()
        writer.writerows(users)
    
    print(f"✅ Generated {len(users)} users in {filename}")

def generate_stations_csv(filename="data/charging_stations.csv"):
    """Generate 120 charging stations"""
    
    # Major US cities with coordinates
    cities = [
        # [city, state, lat, lon]
        ["New York", "NY", 40.7128, -74.0060],
        ["Los Angeles", "CA", 34.0522, -118.2437],
        ["Chicago", "IL", 41.8781, -87.6298],
        ["Houston", "TX", 29.7604, -95.3698],
        ["Phoenix", "AZ", 33.4484, -112.0740],
        ["Philadelphia", "PA", 39.9526, -75.1652],
        ["San Antonio", "TX", 29.4241, -98.4936],
        ["San Diego", "CA", 32.7157, -117.1611],
        ["Dallas", "TX", 32.7767, -96.7970],
        ["San Jose", "CA", 37.3382, -121.8863],
        ["Austin", "TX", 30.2672, -97.7431],
        ["Jacksonville", "FL", 30.3322, -81.6557],
        ["Fort Worth", "TX", 32.7555, -97.3308],
        ["Columbus", "OH", 39.9612, -82.9988],
        ["Charlotte", "NC", 35.2271, -80.8431],
        ["San Francisco", "CA", 37.7749, -122.4194],
        ["Indianapolis", "IN", 39.7684, -86.1581],
        ["Seattle", "WA", 47.6062, -122.3321],
        ["Denver", "CO", 39.7392, -104.9903],
        ["Washington", "DC", 38.9072, -77.0369],
        ["Boston", "MA", 42.3601, -71.0589],
        ["El Paso", "TX", 31.7619, -106.4850],
        ["Nashville", "TN", 36.1627, -86.7816],
        ["Detroit", "MI", 42.3314, -83.0458],
        ["Memphis", "TN", 35.1495, -90.0490],
    ]
    
    stations = []
    station_id = 1000
    
    charger_types = ["DC Fast", "Level 2", "Tesla Supercharger", "CCS Combo", "CHAdeMO"]
    operators = ["Tesla", "Electrify America", "EVgo", "ChargePoint", "Blink", "Volta"]
    
    for city in cities:
        # Generate 5 stations per city (5 * 25 = 125 stations)
        for j in range(5):
            station_id += 1
            
            # Add slight variation to coordinates
            lat = city[2] + random.uniform(-0.1, 0.1)
            lon = city[3] + random.uniform(-0.1, 0.1)
            
            charger_type = random.choice(charger_types)
            operator = random.choice(operators)
            
            # Determine specs based on charger type
            if "Supercharger" in charger_type or "DC Fast" in charger_type:
                power_kw = random.choice([150, 250, 350])
                total_chargers = random.randint(4, 12)
                cost_per_kwh = round(random.uniform(0.35, 0.50), 2)
            else:
                power_kw = random.choice([7.2, 11, 22])
                total_chargers = random.randint(2, 6)
                cost_per_kwh = round(random.uniform(0.20, 0.35), 2)
            
            available_chargers = random.randint(0, total_chargers)
            
            stations.append({
                "station_id": f"STA{station_id:04d}",
                "name": f"{operator} {city[0]} #{j+1}",
                "address": f"{random.randint(100, 9999)} {random.choice(['Main', 'Oak', 'Pine', 'Maple', 'Cedar'])} St",
                "city": city[0],
                "state": city[1],
                "zip_code": f"{random.randint(10000, 99999)}",
                "latitude": round(lat, 6),
                "longitude": round(lon, 6),
                "charger_type": charger_type,
                "operator": operator,
                "available_chargers": available_chargers,
                "total_chargers": total_chargers,
                "power_kw": power_kw,
                "cost_per_kwh": cost_per_kwh,
                "is_24_7": random.choice([True, False]),
                "amenities": json.dumps(random.sample(["Restrooms", "Coffee", "WiFi", "Restaurant", "Shopping", "Waiting Area"], 
                                                    random.randint(1, 4))),
                "rating": round(random.uniform(3.5, 5.0), 1),
                "created_at": datetime.now().isoformat()
            })
    
    with open(filename, 'w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=stations[0].keys())
        writer.writeheader()
        writer.writerows(stations)
    
    print(f"✅ Generated {len(stations)} charging stations in {filename}")

def generate_trips_csv(filename="data/trips.csv"):
    """Generate 150 trips"""
    trips = []
    
    # Create routes between cities
    routes = [
        # [start_city, end_city, approx_distance_km]
        ["New York", "Boston", 340],
        ["Los Angeles", "San Diego", 190],
        ["Chicago", "Indianapolis", 290],
        ["Houston", "Austin", 260],
        ["San Francisco", "San Jose", 70],
        ["Denver", "Colorado Springs", 110],
        ["Seattle", "Portland", 280],
        ["Dallas", "Fort Worth", 50],
        ["Philadelphia", "Washington DC", 220],
        ["Atlanta", "Charlotte", 380],
    ]
    
    for i in range(1, 151):
        route = random.choice(routes)
        start_city, end_city, distance = route
        
        # Generate coordinates around start and end cities
        if start_city == "New York":
            start_lat, start_lon = 40.7128 + random.uniform(-0.05, 0.05), -74.0060 + random.uniform(-0.05, 0.05)
        elif start_city == "Los Angeles":
            start_lat, start_lon = 34.0522 + random.uniform(-0.05, 0.05), -118.2437 + random.uniform(-0.05, 0.05)
        elif start_city == "Chicago":
            start_lat, start_lon = 41.8781 + random.uniform(-0.05, 0.05), -87.6298 + random.uniform(-0.05, 0.05)
        elif start_city == "Houston":
            start_lat, start_lon = 29.7604 + random.uniform(-0.05, 0.05), -95.3698 + random.uniform(-0.05, 0.05)
        elif start_city == "San Francisco":
            start_lat, start_lon = 37.7749 + random.uniform(-0.05, 0.05), -122.4194 + random.uniform(-0.05, 0.05)
        elif start_city == "Denver":
            start_lat, start_lon = 39.7392 + random.uniform(-0.05, 0.05), -104.9903 + random.uniform(-0.05, 0.05)
        elif start_city == "Seattle":
            start_lat, start_lon = 47.6062 + random.uniform(-0.05, 0.05), -122.3321 + random.uniform(-0.05, 0.05)
        elif start_city == "Dallas":
            start_lat, start_lon = 32.7767 + random.uniform(-0.05, 0.05), -96.7970 + random.uniform(-0.05, 0.05)
        elif start_city == "Philadelphia":
            start_lat, start_lon = 39.9526 + random.uniform(-0.05, 0.05), -75.1652 + random.uniform(-0.05, 0.05)
        else:  # Atlanta
            start_lat, start_lon = 33.7490 + random.uniform(-0.05, 0.05), -84.3880 + random.uniform(-0.05, 0.05)
        
        if end_city == "Boston":
            end_lat, end_lon = 42.3601 + random.uniform(-0.05, 0.05), -71.0589 + random.uniform(-0.05, 0.05)
        elif end_city == "San Diego":
            end_lat, end_lon = 32.7157 + random.uniform(-0.05, 0.05), -117.1611 + random.uniform(-0.05, 0.05)
        elif end_city == "Indianapolis":
            end_lat, end_lon = 39.7684 + random.uniform(-0.05, 0.05), -86.1581 + random.uniform(-0.05, 0.05)
        elif end_city == "Austin":
            end_lat, end_lon = 30.2672 + random.uniform(-0.05, 0.05), -97.7431 + random.uniform(-0.05, 0.05)
        elif end_city == "San Jose":
            end_lat, end_lon = 37.3382 + random.uniform(-0.05, 0.05), -121.8863 + random.uniform(-0.05, 0.05)
        elif end_city == "Colorado Springs":
            end_lat, end_lon = 38.8339 + random.uniform(-0.05, 0.05), -104.8214 + random.uniform(-0.05, 0.05)
        elif end_city == "Portland":
            end_lat, end_lon = 45.5152 + random.uniform(-0.05, 0.05), -122.6784 + random.uniform(-0.05, 0.05)
        elif end_city == "Fort Worth":
            end_lat, end_lon = 32.7555 + random.uniform(-0.05, 0.05), -97.3308 + random.uniform(-0.05, 0.05)
        elif end_city == "Washington DC":
            end_lat, end_lon = 38.9072 + random.uniform(-0.05, 0.05), -77.0369 + random.uniform(-0.05, 0.05)
        else:  # Charlotte
            end_lat, end_lon = 35.2271 + random.uniform(-0.05, 0.05), -80.8431 + random.uniform(-0.05, 0.05)
        
        # Add some random variation to distance
        actual_distance = distance * random.uniform(0.9, 1.1)
        
        trips.append({
            "trip_id": f"trip_{i:04d}",
            "user_id": f"user_{(i % 60) + 1:03d}",
            "car_id": f"car_{(i % 80) + 1:03d}",
            "start_latitude": round(start_lat, 6),
            "start_longitude": round(start_lon, 6),
            "end_latitude": round(end_lat, 6),
            "end_longitude": round(end_lon, 6),
            "start_address": f"{random.randint(100, 999)} {random.choice(['Main', 'Oak'])} St, {start_city}",
            "end_address": f"{random.randint(100, 999)} {random.choice(['Maple', 'Pine'])} Ave, {end_city}",
            "distance_km": round(actual_distance, 2),
            "estimated_energy_kwh": round(actual_distance * random.uniform(0.15, 0.25), 2),
            "actual_energy_kwh": round(actual_distance * random.uniform(0.14, 0.26), 2),
            "duration_minutes": round((actual_distance / 80) * 60),  # 80 km/h average
            "start_time": (datetime.now() - timedelta(days=random.randint(1, 30))).isoformat(),
            "end_time": (datetime.now() - timedelta(days=random.randint(1, 30), hours=random.randint(1, 5))).isoformat(),
            "charging_stops": random.randint(0, 2),
            "total_charging_time_minutes": random.randint(0, 60),
            "cost_usd": round(actual_distance * random.uniform(0.05, 0.15), 2),
            "weather": random.choice(["Clear", "Rainy", "Cloudy", "Windy"]),
            "notes": random.choice(["", "Smooth trip", "Traffic delays", "Charged at station"])
        })
    
    with open(filename, 'w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=trips[0].keys())
        writer.writeheader()
        writer.writerows(trips)
    
    print(f"✅ Generated {len(trips)} trips in {filename}")

if __name__ == "__main__":
    print("🚀 Generating sample data...")
    generate_users_csv()
    def generate_cars_csv(filename="data/cars.csv"):
        """Generate 80 cars"""
        ensure_directory(filename)
        cars = []
        
        # Generate 80 cars
        for i in range(1, 81):
            cars.append({
                "car_id": f"car_{i:03d}",
                "make": random.choice(["Tesla", "Nissan", "Chevrolet", "BMW", "Hyundai", "Kia"]),
                "model": random.choice(["Model S", "Leaf", "Bolt", "i3", "Kona", "Soul"]),
                "year": random.randint(2015, 2023),
                "battery_capacity_kwh": random.choice([40, 60, 75, 100]),
                "range_km": random.randint(150, 500),
                "charging_speed_kw": random.choice([50, 100, 150]),
                "created_at": datetime.now().isoformat()
            })
        
        # Write to CSV
        with open(filename, 'w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=cars[0].keys())
            writer.writeheader()
            writer.writerows(cars)
        
        print(f"✅ Generated {len(cars)} cars in {filename}")
    
        generate_cars_csv()
    generate_stations_csv()
    generate_trips_csv()
    print("🎉 All sample data generated successfully!")
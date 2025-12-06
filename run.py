#!/usr/bin/env python3
"""
EV Charging Assistant - Startup Script
"""
import subprocess
import sys
import os

def check_dependencies():
    """Check if all required packages are installed"""
    try:
        import fastapi
        import uvicorn
        import pymongo
        import pandas
        print("✅ All dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please run: pip install -r requirements.txt")
        return False

def check_mongodb():
    """Check if MongoDB is running"""
    try:
        import pymongo
        client = pymongo.MongoClient("mongodb+srv://subh_25:12345SH@evcharging.gyy7knt.mongodb.net/?retryWrites=true&w=majority", serverSelectionTimeoutMS=5000)
        client.admin.command('ping')
        print("✅ MongoDB is running")
        return True
    except Exception as e:
        print(f"❌ MongoDB is not running: {e}")
        print("Please start MongoDB with: mongod or docker-compose up -d mongodb")
        return False

def generate_sample_data():
    """Generate sample data if needed"""
    if not os.path.exists("data/users.csv"):
        print("📊 Generating sample data...")
        try:
            from scripts.generate_data import generate_users_csv, generate_cars_csv, generate_stations_csv, generate_trips_csv
            generate_users_csv()
            generate_cars_csv()
            generate_stations_csv()
            generate_trips_csv()
            print("✅ Sample data generated")
        except Exception as e:
            print(f"❌ Error generating sample data: {e}")
            return False
    else:
        print("✅ Sample data already exists")
    return True

def load_data_to_mongodb():
    """Load CSV data to MongoDB"""
    print("📥 Loading data to MongoDB...")
    try:
        from app.utils.data_loader import load_csv_to_mongodb
        load_csv_to_mongodb()
        print("✅ Data loaded to MongoDB")
        return True
    except Exception as e:
        print(f"❌ Error loading data to MongoDB: {e}")
        return False

def main():
    """Main startup function"""
    print("=" * 60)
    print("🚗 EV Charging Assistant - Starting Up")
    print("=" * 60)
    
    # Step 1: Check dependencies
    print("\n1. Checking dependencies...")
    if not check_dependencies():
        sys.exit(1)
    
    # Step 2: Check MongoDB
    print("\n2. Checking MongoDB...")
    if not check_mongodb():
        print("⚠️  Starting API anyway, but database features may not work")
    
    # Step 3: Generate sample data
    print("\n3. Checking sample data...")
    generate_sample_data()
    
    # Step 4: Load data to MongoDB
    print("\n4. Loading data to MongoDB...")
    load_data_to_mongodb()
    
    # Step 5: Start the API
    print("\n5. Starting FastAPI server...")
    print("=" * 60)
    print("✅ EV Charging Assistant is ready!")
    print("🌐 API Documentation: http://localhost:8000/docs")
    print("📊 Dashboard: http://localhost:8000/dashboard/stats")
    print("🔄 Auto-reload: Enabled")
    print("=" * 60)
    
    # Start uvicorn
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

if __name__ == "__main__":
    main()
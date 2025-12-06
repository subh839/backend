from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.database import mongodb
from app.auth import get_current_user
import logging

# Import routers directly
from app.routers.auth import router as auth_router
from app.routers.cars import router as cars_router
from app.routers.stations import router as stations_router
from app.routers.trips import router as trips_router
from app.routers.suggestions import router as suggestions_router
from app.routers.dashboard import router as dashboard_router

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("🚀 Starting EV Charging Assistant API...")
    await mongodb.connect_to_mongo()
    logger.info("✅ Database connected and indexes created")
    
    yield
    
    # Shutdown
    await mongodb.close_mongo_connection()
    logger.info("👋 Shutting down EV Charging Assistant API")

app = FastAPI(
    title="EV Charging Assistant API",
    description="A comprehensive API for electric vehicle charging assistance with route planning, station finding, and driver suggestions",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(cars_router)
app.include_router(stations_router)
app.include_router(trips_router)
app.include_router(suggestions_router)
app.include_router(dashboard_router)

@app.get("/")
async def root():
    return {
        "message": "🚗 EV Charging Assistant API",
        "version": "2.0.0",
        "description": "Electric Vehicle Charging Assistance System",
        "features": [
            "User Authentication & Management",
            "Car Profile Management",
            "Charging Station Finder",
            "Route Planning with Range Calculation",
            "Intelligent Driver Suggestions",
            "Trip History & Analytics",
            "Interactive Dashboard"
        ],
        "endpoints": {
            "documentation": "/docs",
            "authentication": "/auth",
            "cars": "/cars",
            "stations": "/stations",
            "trips": "/trips",
            "suggestions": "/suggestions",
            "dashboard": "/dashboard"
        },
        "status": "operational",
        "database": "connected"
    }

@app.get("/health")
async def health_check():
    """Public route - Health check"""
    return {"status": "healthy", "service": "EV Charging Assistant API"}

@app.get("/api/status")
async def api_status():
    """Check API and database status"""
    try:
        from app.database import mongodb
        # Try to ping database
        await mongodb.client.admin.command('ping')
        db_status = "connected"
    except:
        db_status = "disconnected"
    
    return {
        "api": "running",
        "database": db_status,
        "version": "2.0.0",
        "uptime": "0 days 0 hours"
    }

# Admin endpoints for data management
@app.post("/admin/load-data")
async def load_data_from_csv(
    data_type: str = "all",
    current_user: dict = Depends(get_current_user)
):
    """Protected admin route to load data from CSV"""
    from app.utils.data_loader import load_csv_to_mongodb
    
    try:
        load_csv_to_mongodb()
        return {
            "message": "Data loaded successfully",
            "data_type": data_type,
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading data: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
from app.config import settings

class MongoDB:
    client: AsyncIOMotorClient = None
    
    async def connect_to_mongo(self):
        self.client = AsyncIOMotorClient(settings.mongodb_url)
        print("✅ Connected to MongoDB")
        
        # Create indexes
        await self.create_indexes()
    
    async def create_indexes(self):
        db = self.get_database()
        # Create geospatial index for stations
        await db.charging_stations.create_index([("location", "2dsphere")])
        # Create unique indexes for users
        await db.users.create_index([("email", 1)], unique=True)
        await db.users.create_index([("username", 1)], unique=True)
        print("✅ Database indexes created")
    
    async def close_mongo_connection(self):
        if self.client:
            self.client.close()
            print("✅ Closed MongoDB connection")
    
    def get_database(self):
        return self.client[settings.database_name]

mongodb = MongoDB()

def get_sync_client():
    """For synchronous operations like data loading"""
    return MongoClient(settings.mongodb_url)[settings.database_name]
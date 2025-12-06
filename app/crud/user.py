from app.database import mongodb
from app.auth import get_password_hash, verify_password
from bson import ObjectId

async def create_user(user_data: dict):
    db = mongodb.get_database()
    user_data["hashed_password"] = get_password_hash(user_data["password"])
    del user_data["password"]
    user_data["is_active"] = True
    user_data["role"] = "user"
    
    result = await db.users.insert_one(user_data)
    return str(result.inserted_id)

async def get_user_by_email(email: str):
    db = mongodb.get_database()
    user = await db.users.find_one({"email": email})
    if user:
        user["id"] = str(user["_id"])
    return user

async def get_user_by_id(user_id: str):
    db = mongodb.get_database()
    try:
        user = await db.users.find_one({"_id": ObjectId(user_id)})
        if user:
            user["id"] = str(user["_id"])
        return user
    except:
        return None

async def authenticate_user(email: str, password: str):
    user = await get_user_by_email(email)
    if not user:
        return False
    if not verify_password(password, user["hashed_password"]):
        return False
    return user
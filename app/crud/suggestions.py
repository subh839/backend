from app.database import mongodb
from bson import ObjectId
from datetime import datetime

async def save_suggestion_feedback(user_id: str, suggestion_id: str, was_helpful: bool, feedback_text: str = ""):
    db = mongodb.get_database()
    
    feedback = {
        "user_id": user_id,
        "suggestion_id": suggestion_id,
        "was_helpful": was_helpful,
        "feedback_text": feedback_text,
        "created_at": datetime.utcnow()
    }
    
    result = await db.suggestion_feedback.insert_one(feedback)
    return str(result.inserted_id)
from pydantic import BaseModel, EmailStr, ConfigDict, Field
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: Optional[str] = None
    phone: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

# FIXED: Updated User model to match MongoDB
class User(UserBase):
    id: str = Field(alias="_id")  # Maps MongoDB '_id' to 'id'
    # REMOVED: user_id field (duplicate of id)
    is_active: bool = True
    role: str = "user"
    # Make created_at optional since it doesn't exist in your MongoDB
    created_at: Optional[datetime] = None
    
    model_config = ConfigDict(
        populate_by_name=True,  # Important for field mapping
        from_attributes=True
    )

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None
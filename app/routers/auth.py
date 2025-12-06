from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from bson import ObjectId
from app.schemas.user import UserCreate, User, Token
from app.crud.user import create_user, authenticate_user, get_user_by_email
from app.auth import create_access_token, get_current_user
from app.config import settings

router = APIRouter(prefix="/auth", tags=["authentication"])

@router.post("/register", response_model=dict)
async def register(user: UserCreate):
    """Register a new user"""
    existing_user = await get_user_by_email(user.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    user_data = user.dict()
    user_id = await create_user(user_data)
    return {"message": "User created successfully", "user_id": user_id}

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login user and get access token"""
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user["email"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# FIXED: /auth/me endpoint
@router.get("/me", response_model=User)
async def read_users_me(current_user: dict = Depends(get_current_user)):
    """Get current user info"""
    # Create a mutable copy
    user_data = current_user.copy()
    
    # Convert ObjectId to string
    if "_id" in user_data and isinstance(user_data["_id"], ObjectId):
        user_data["_id"] = str(user_data["_id"])
    
    # Add default values for optional fields if they don't exist
    if "is_active" not in user_data:
        user_data["is_active"] = True
    if "role" not in user_data:
        user_data["role"] = "user"
    if "created_at" not in user_data:
        user_data["created_at"] = None  # or datetime.utcnow() if you want to set it
    
    # The Pydantic User model will map "_id" to "id" because of alias="_id"
    # Also, populate_by_name=True allows using either "_id" or "id"
    return User(**user_data)  # Explicitly create User instance
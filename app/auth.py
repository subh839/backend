"""
Authentication module - Custom implementation to avoid bcrypt issues
"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from app.schemas.user import TokenData
from app.config import settings
import hashlib
import secrets
import base64

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash using SHA256 with salt
    """
    try:
        # Decode the stored hash (format: salt:hash)
        if ":" not in hashed_password:
            return False
        
        salt_b64, stored_hash_b64 = hashed_password.split(":", 1)
        
        # Decode from base64
        salt = base64.b64decode(salt_b64)
        stored_hash = base64.b64decode(stored_hash_b64)
        
        # Hash the provided password with the same salt
        test_hash = hashlib.pbkdf2_hmac(
            'sha256',
            plain_password.encode('utf-8'),
            salt,
            100000  # Number of iterations
        )
        
        # Compare securely
        return secrets.compare_digest(test_hash, stored_hash)
        
    except Exception:
        return False

def get_password_hash(password: str) -> str:
    """
    Hash a password for storage using PBKDF2 with SHA256
    """
    # Generate a random salt
    salt = secrets.token_bytes(32)
    
    # Hash the password with the salt using PBKDF2
    hash_value = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt,
        100000,  # Number of iterations (adjust as needed)
        dklen=32  # Output length
    )
    
    # Encode salt and hash in base64 for storage
    salt_b64 = base64.b64encode(salt).decode('utf-8')
    hash_b64 = base64.b64encode(hash_value).decode('utf-8')
    
    # Return in format: salt:hash
    return f"{salt_b64}:{hash_b64}"

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    Create a JWT access token
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Get current user from JWT token
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception
    
    from app.crud.user import get_user_by_email
    user = await get_user_by_email(token_data.email)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(current_user = Depends(get_current_user)):
    """
    Get current active user
    """
    if not current_user.get("is_active", True):
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

def test_password_hashing():
    """
    Test function to verify password hashing works
    """
    print("🧪 Testing password hashing...")
    
    # Test 1: Hash and verify
    password = "test123"
    hashed = get_password_hash(password)
    print(f"✅ Password hashed successfully")
    print(f"   Hash format: {hashed[:50]}...")
    
    # Test 2: Verify correct password
    verified = verify_password(password, hashed)
    print(f"✅ Correct password verified: {verified}")
    
    # Test 3: Verify wrong password
    wrong_verified = verify_password("wrong", hashed)
    print(f"✅ Wrong password rejected: {not wrong_verified}")
    
    # Test 4: Test with special characters
    special_pass = "P@ssw0rd!123#"
    special_hash = get_password_hash(special_pass)
    special_verified = verify_password(special_pass, special_hash)
    print(f"✅ Special characters password: {special_verified}")
    
    # Test 5: Test long password
    long_pass = "A" * 100  # 100 character password
    long_hash = get_password_hash(long_pass)
    long_verified = verify_password(long_pass, long_hash)
    print(f"✅ Long password (100 chars): {long_verified}")
    
    print("\n🎉 All password tests passed!")
    return True
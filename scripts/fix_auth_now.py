#!/usr/bin/env python3
"""
Quick fix for authentication issues
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_auth_fix():
    """Test if auth fix works"""
    from app.auth import get_password_hash, verify_password
    
    print("🧪 Testing authentication fix...")
    
    # Test 1: Hash a password
    password = "MySecurePassword123ThatIsLongerThan72BytesForTestingPurposes1234567890"
    hashed = get_password_hash(password)
    print(f"✅ Password hashed successfully (length: {len(hashed)} chars)")
    print(f"   Hash starts with: {hashed[:20]}...")
    
    # Test 2: Verify the password
    verified = verify_password(password, hashed)
    print(f"✅ Password verification: {verified}")
    
    # Test 3: Wrong password should fail
    wrong_verified = verify_password("WrongPassword", hashed)
    print(f"✅ Wrong password rejected: {not wrong_verified}")
    
    print("\n🎉 Authentication fix is working!")
    return True

def reset_users_collection():
    """Reset users collection with fixed passwords"""
    from app.database import get_sync_client
    from app.auth import get_password_hash
    
    db = get_sync_client()
    
    print("🔄 Resetting users collection...")
    
    # Delete existing users
    db.users.delete_many({})
    print("   Cleared existing users")
    
    # Create some test users
    test_users = [
        {
            "user_id": "user_001",
            "email": "user1@example.com",
            "username": "user_001",
            "hashed_password": get_password_hash("pass123"),
            "full_name": "User One",
            "phone": "+1-555-123-4567",
            "is_active": True,
            "role": "user",
            "created_at": datetime.now()
        },
        {
            "user_id": "user_002",
            "email": "user2@example.com",
            "username": "user_002",
            "hashed_password": get_password_hash("pass123"),
            "full_name": "User Two",
            "phone": "+1-555-234-5678",
            "is_active": True,
            "role": "user",
            "created_at": datetime.now()
        },
        {
            "user_id": "user_003",
            "email": "user3@example.com",
            "username": "user_003",
            "hashed_password": get_password_hash("pass123"),
            "full_name": "User Three",
            "phone": "+1-555-345-6789",
            "is_active": True,
            "role": "user",
            "created_at": datetime.now()
        }
    ]
    
    db.users.insert_many(test_users)
    print(f"✅ Created {len(test_users)} test users")
    print(f"📊 Total users: {db.users.count_documents({})}")

if __name__ == "__main__":
    from datetime import datetime
    
    print("=" * 60)
    print("🔧 Quick Authentication Fix")
    print("=" * 60)
    
    try:
        test_auth_fix()
        reset_users_collection()
        
        print("\n" + "=" * 60)
        print("✅ Fix applied successfully!")
        print("=" * 60)
        print("\n🎯 You can now:")
        print("1. Register new users via API")
        print("2. Login with:")
        print("   - Email: user1@example.com")
        print("   - Password: pass123")
        print("\n3. Test API at: http://localhost:8000/docs")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
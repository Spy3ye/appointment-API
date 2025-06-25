# services/User.py
from typing import List, Optional, Dict, Any
from uuid import UUID
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException, status , Depends
from schemas.User import UserCreate, UserUpdate, UserOut
from models.User import User, UserRole
import uuid
from utils.auth import hash_password, verify_password
from database.database import get_database
#hi
class UserService:
    
    @staticmethod
    async def create_user(
        user: UserCreate, 
        db: AsyncIOMotorDatabase = Depends(get_database)
        ):    
     try:
        print(f"Starting user creation for email: {user.email}")

        # Optional: check if user exists
        existing_user = await db["users"].find_one({"email": user.email})
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists"
            )

        print("Creating new user object...")
        user_dict = {
            "name": user.name,
            "email": user.email,
            "phone":user.phone,
            "hashed_password": hash_password(user.password),
            "role": UserRole.customer,
            "is_active": True
        }

        result = await db["users"].insert_one(user_dict)
        user_dict["id"] = str(result.inserted_id)
        user_dict["phone"] = user.phone 

        print("User inserted successfully")
        return UserOut(**user_dict)
     except Exception as e:
        print(f"Error creating user: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")
    
    @staticmethod
    async def authenticate_user(email: str, password: str , db: AsyncIOMotorDatabase) -> UserOut:
        user = await db["users"].find_one({"email":email})
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Fixed password verification logic
        if not verify_password(password, user["hashed_password"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        user["id"] = str(user["_id"])
        user.pop("_id", None)
        
        return UserOut(**user)
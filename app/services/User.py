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
            "hashed_password": hash_password(user.password),
            "role": user_role,
            "is_active": True
        }

        result = await db["users"].insert_one(user_dict)
        user_dict["id"] = str(result.inserted_id)

        print("User inserted successfully")
        return UserOut(**user_dict)
     except Exception as e:
        print(f"Error creating user: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")
    
    @staticmethod
    async def authenticate_user(db: AsyncIOMotorDatabase, email: str, password: str) -> UserOut:
        user = await User.by_email(email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Fixed password verification logic
        if not verify_password(password=password, hashed_password=user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        return UserOut(
            id=str(user.id) if hasattr(user, 'id') else None,
            name=user.name,
            email=user.email,
            role=user.role,
            is_active=user.is_active
        )
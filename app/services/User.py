# services/User.py
from typing import List, Optional, Dict, Any
from uuid import UUID
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException, status , Depends
from schemas.User import UserCreate, UserUpdate, UserOut
from models.User import User, UserRole
import uuid
from utils.auth import hash_password, verify_password
from app.database.database import db

class UserService:
    
    @staticmethod
    async def create_user(user: UserCreate, user_role: UserRole = UserRole.customer , db_session=Depends(db)) -> UserOut:
        try:
            print(f"Starting user creation for email: {user.email}")
            
            # TEMPORARILY SKIP DUPLICATE CHECK - UNCOMMENT AFTER FIXING MODEL
            # print("Checking for existing user...")
            # existing_user = await User.find_one({"email": user.email})
            # if existing_user:
            #     raise HTTPException(
            #         status_code=status.HTTP_400_BAD_REQUEST,
            #         detail="User with this email already exists"
            #     )
            
            print("Creating new user object...")
            # Create new user
            user_in = User(
                name=user.name,
                email=user.email,
                hashed_password=hash_password(user.password),
                role=user_role,
                is_active=True
            )
            
            # print("Inserting user into database...")
            # Try different insert methods
            # try:
            db_session.insert(user_in)
            # except AttributeError:
            user_in.save(db_session)
            
            # print("User inserted successfully")
            
            # Return UserOut with the created user data
            # user_out = UserOut(
            #     id=str(user_in.id) if hasattr(user_in, 'id') else None,
            #     name=user_in.name,
            #     email=user_in.email,
            #     role=user_in.role,
            #     is_active=user_in.is_active
            # )
            # print(f"Returning user_out: {user_out}")
            return user_in
            
        except HTTPException:
            raise
        except Exception as e:
            print(f"Error in create_user service: {str(e)}")
            print(f"Error type: {type(e).__name__}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            raise
    
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
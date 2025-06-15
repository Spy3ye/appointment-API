from typing import List, Optional, Dict, Any
from uuid import UUID
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException, status
# from passlib.context import CryptContext
from schemas.User import UserCreate, UserUpdate, UserOut
from models.User import User, UserRole
import uuid
from utils.auth import hash_password , verify_password
# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserService:
    async def create_user(db:AsyncIOMotorDatabase, user_data:UserCreate , UserRole = UserRole.customer) -> UserOut:
        existing_user = await db.users.find_one({"email":user_data.email})
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists"
            )
        
        
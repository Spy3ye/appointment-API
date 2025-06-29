from bson import ObjectId
from typing import Optional
from fastapi import HTTPException, status , Depends
from database.collections import get_user_collection
from database.database import get_database
from schemas.User import UserCreate, UserOut
from models.User import User, UserRole
from utils.auth import hash_password, verify_password, create_access_token, create_refresh_token, decode_access_token
from datetime import timedelta
from motor.motor_asyncio import AsyncIOMotorDatabase



class AuthService:
    # async def login_user(self, email: str, password: str) -> dict:
    #     """Login user and return tokens"""
    #     user = await self.authenticate_user(email, password)
    #     if not user:
    #         raise HTTPException(
    #             status_code=status.HTTP_401_UNAUTHORIZED,
    #             detail="Incorrect email or password",
    #             headers={"WWW-Authenticate": "Bearer"},
    #         )
        
    #     # Create tokens
    #     access_token_expires = timedelta(minutes=30)
    #     access_token = create_access_token(
    #         data={"sub": user["email"], "user_id": str(user["_id"]), "role": user["role"]},
    #         expires_delta=access_token_expires
    #     )
    #     refresh_token = create_refresh_token(subject=user["email"])
        
    #     return {
    #         "access_token": access_token,
    #         "refresh_token": refresh_token,
    #         "token_type": "bearer",
    #         "user": UserOut(**user)
    #     }

    async def get_current_user(db : AsyncIOMotorDatabase = Depends(get_database), token: str) -> dict:
        """Get current user from token"""
        try:
            payload = decode_access_token(token)
            email: str = payload.get("sub")
            if email is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Could not validate credentials",
                    headers={"WWW-Authenticate": "Bearer"},
                )
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        user = await self.collection.find_one({"email": email})
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        user["id"] = str(user["_id"])
        return user

    async def refresh_access_token(db:AsyncIOMotorDatabase=Depends(get_database), refresh_token: str) -> dict:
        """Refresh access token using refresh token"""
        try:
            # Decode refresh token (you'll need to implement this in auth.py)
            payload = decode_access_token(refresh_token)  # Note: You might want a separate function for refresh tokens
            email: str = payload.get("sub")
            if email is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid refresh token"
                )
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        # Get user
        user = await self.collection.find_one({"email": email})
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        # Create new access token
        access_token_expires = timedelta(minutes=30)
        access_token = create_access_token(
            data={"sub": user["email"], "user_id": str(user["_id"]), "role": user["role"]},
            expires_delta=access_token_expires
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer"
        }

    async def change_password(self, user_id: str, old_password: str, new_password: str) -> bool:
        """Change user password"""
        user = await self.collection.find_one({"_id": ObjectId(user_id)})
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Verify old password
        if not verify_password(old_password, user["hashed_password"]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Incorrect old password"
            )
        
        # Hash new password
        new_hashed_password = hash_password(new_password)
        
        # Update password
        result = await self.collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"hashed_password": new_hashed_password}}
        )
        
        return result.modified_count > 0

    async def deactivate_user(self, user_id: str) -> bool:
        """Deactivate user account"""
        result = await self.collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"is_active": False}}
        )
        return result.modified_count > 0

    async def activate_user(db:AsyncIOMotorDatabase=Depends(get_database), user_id: str) -> bool:
        """Activate user account"""
        result = await self.collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"is_active": True}}
        )
        return result.modified_count > 0


auth_service = AuthService()



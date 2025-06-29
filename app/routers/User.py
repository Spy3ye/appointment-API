# routes/user.py
from fastapi import APIRouter, Depends, HTTPException, status
from schemas.User import UserCreate, UserOut
from services.User import UserService
from models.User import User
import traceback
from database.database import get_database
from motor.motor_asyncio import AsyncIOMotorDatabase


user_router = APIRouter()

@user_router.post("/create", summary="Create new user", response_model=UserOut)
async def create_user(
    user_data: UserCreate, 
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    try:
        # print(f"Received data: {user_data}")  

        
        user = await UserService.create_user(user_data,db)  

        # print(f"User created successfully: {user}")  

        # User.save(db)

        return user

    except HTTPException as http_exc:
        print(f"HTTP Exception: {http_exc.detail}")
        raise http_exc

    except Exception as e:
        print(f"Full error: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )
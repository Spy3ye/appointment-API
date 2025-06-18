# routes/user.py
from fastapi import APIRouter, Depends, HTTPException, status
from schemas.User import UserCreate, UserOut
from services.User import UserService
from models.User import User
import traceback
from app.database.database import db

user_router = APIRouter()

@user_router.post("/create", summary="Create new user", response_model=UserOut)
async def create_user(data: UserCreate , db_session=db):
    try:
        print(f"Received data: {data}")  # Debug log
        user = await UserService.create_user(data)
        print(f"User created successfully: {user}")  # Debug log
        User.save(db_session)
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
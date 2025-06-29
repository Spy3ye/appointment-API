from fastapi import HTTPException, status , Depends , APIRouter
from utils.auth import create_access_token , create_refresh_token
from models.User import User
from services.User import UserService
from fastapi.security import OAuth2PasswordRequestForm
from schemas.User import UserOut , UserIn
from database.database import get_database
from database.collections import get_user_collection
from motor.motor_asyncio import AsyncIOMotorDatabase
# from utils.auth import hash_password, verify_password , create_access_token, create_refresh_token


auth_router = APIRouter()

@auth_router.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> UserOut:
    user = await UserService.authenticate_user(
        email=form_data.username,
        password=form_data.password,
        db=db,
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Wrong email or password",
        )

    return user
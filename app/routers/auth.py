from fastapi import HTTPException, status , Depends , APIRouter
from utils.auth import create_access_token , create_refresh_token
from models.User import User
from services.User import UserService
from fastapi.security import OAuth2PasswordRequestForm
from schemas.User import UserOut
from database.database import get_database
from motor.motor_asyncio import AsyncIOMotorDatabase


auth_router = APIRouter()

@auth_router.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
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

    access_token = create_access_token({"sub":str(user.id)})
    refresh_token = create_refresh_token({"sub":str(user.id)})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }
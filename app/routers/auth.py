from fastapi import HTTPException, status , Depends , APIRouter
from utils.auth import create_access_token , create_refresh_token
from models.User import User
from services.User import UserService
from fastapi.security import OAuth2PasswordRequestForm
from schemas.User import UserOut

auth_router = APIRouter()



@auth_router.post("/login" , response_model=UserOut)
async def login(form_data:OAuth2PasswordRequestForm =Depends()) -> any:
    
    user = await UserService.authenticate_user(
        email = form_data.email,
        password = form_data.password
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="wrong email or password"
        )
    access_token = create_access_token(str(user.id))
    refresh_token = create_refresh_token(str(user.id))
    
    return {
        "access token " : access_token,
        "refresh token" : refresh_token,
        "token type" : "bearer"
        }
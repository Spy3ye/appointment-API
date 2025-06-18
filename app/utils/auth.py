from passlib.context import CryptContext
from jose import JWTError, jwt
import os
from datetime import datetime, timedelta
from config import MONGO_URI , ALGORITHM , SECRET_REFRESH_KEY , SECRET_KEY

# load_dotenv()

# SECRET_KEY = os.getenv("SECRET_KEY")
# ALGORITHM = os.getenv("HS256")
# SECRET_REFRESH_KEY = os.getenv("SECRET_REFRESH_KEY")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.now() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_access_token(token: str):
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

def create_refresh_token(subject: str) -> str:
    expires = datetime.now() + timedelta(days=7)
    to_encode = {"sub":subject , "exp": int(expires.timestamp())}
    return jwt.encode(to_encode,SECRET_REFRESH_KEY , algorithm=ALGORITHM)
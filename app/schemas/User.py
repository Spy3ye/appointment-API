from pydantic import BaseModel, EmailStr , Field
from uuid import UUID
from typing import Optional
from models.User import User

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    password: str

class UserUpdate(BaseModel):
    name: Optional[str]
    phone: Optional[str] = None
    password: Optional[str]

class UserIn(BaseModel):
    email: EmailStr
    hashed_password: Optional[str] = None
    
    model_config = {
        "from_attributes": True  # ✅ instead of orm_mode = True
    }

class UserOut(BaseModel):
    id: str = Field(alias="_id") 
    name: str
    email: EmailStr
    phone: str
    access_token: str
    refresh_token: str
    token_type: str

    model_config = {
        "from_attributes": True  # ✅ instead of orm_mode = True
        # "allow_population_by_field_name" = True
    }

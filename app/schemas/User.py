from pydantic import BaseModel, EmailStr
from uuid import UUID
from typing import Optional
from models.User import User

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str]
    password: str

class UserUpdate(BaseModel):
    name: Optional[str]
    phone: Optional[str]
    password: Optional[str]

class UserOut(BaseModel):
    id: UUID
    name: str
    email: EmailStr
    phone: Optional[str]

    model_config = {
        "from_attributes": True  # ✅ instead of orm_mode = True
    }

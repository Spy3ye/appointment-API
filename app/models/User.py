from pydantic import BaseModel , EmailStr , Field
from uuid import UUID , uuid4
from typing import Literal
from enum import Enum

class UserRole(str,Enum):
    admin = "admin"
    clinic_manager = "clinic manager"
    staff = "staff"
    customer = "customer"

class User(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    name: str
    email: EmailStr
    hashed_password: str
    role: UserRole.customer
    is_active: bool

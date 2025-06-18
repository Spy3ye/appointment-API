from pydantic import BaseModel, EmailStr, Field
from uuid import UUID, uuid4
from typing import Literal
from enum import Enum

class UserRole(str, Enum):
    admin = "admin"
    clinic_manager = "clinic manager"
    staff = "staff"
    customer = "customer"

class User(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    name: str
    email: EmailStr
    hashed_password: str
    role: UserRole = UserRole.customer  # Fixed: Set default value properly
    is_active: bool = True  # Added default value for is_active
    def save(self, db_session):
        """Custom save method"""
        # Convert to SQLAlchemy model or execute raw SQL
        # This is just an example - implement based on your database setup
        pass

# Alternative approaches for the role field:

# # Option 1: No default (role must be provided)
# class UserV1(BaseModel):
#     id: UUID = Field(default_factory=uuid4)
#     name: str
#     email: EmailStr
#     hashed_password: str
#     role: UserRole  # No default
#     is_active: bool = True

# # Option 2: Using Field with default
# class UserV2(BaseModel):
#     id: UUID = Field(default_factory=uuid4)
#     name: str
#     email: EmailStr
#     hashed_password: str
#     role: UserRole = Field(default=UserRole.customer)
#     is_active: bool = True

# # Option 3: Using Literal for specific roles only (if you want to restrict)
# class CustomerUser(BaseModel):
#     id: UUID = Field(default_factory=uuid4)
#     name: str
#     email: EmailStr
#     hashed_password: str
#     role: Literal[UserRole.customer] = UserRole.customer
#     is_active: bool = True
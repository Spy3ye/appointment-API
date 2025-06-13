from pydantic import BaseModel, EmailStr
from uuid import UUID
from typing import Optional

class ClinicCreate(BaseModel):
    name: str
    address: str
    phone: Optional[str]

class ClinicUpdate(BaseModel):
    name: Optional[str]
    address: Optional[str]
    phone: Optional[str]

class ClinicOut(BaseModel):
    id: UUID
    name: str
    address: str
    phone: Optional[str]

    class Config:
        orm_mode = True

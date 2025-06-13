from pydantic import BaseModel, EmailStr
from uuid import UUID
from typing import Optional

class ServiceCreate(BaseModel):
    name: str
    duration_minutes: int
    price: float

class ServiceUpdate(BaseModel):
    name: Optional[str]
    duration_minutes: Optional[int]
    price: Optional[float]

class ServiceOut(BaseModel):
    id: UUID
    name: str
    duration_minutes: int
    price: float

    class Config:
        orm_mode = True

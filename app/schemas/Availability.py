from pydantic import BaseModel, EmailStr
from uuid import UUID
from typing import Optional
from datetime import datetime

class AvailabilityCreate(BaseModel):
    staff_id: UUID
    start_time: datetime
    end_time: datetime

class AvailabilityUpdate(BaseModel):
    start_time: Optional[datetime]
    end_time: Optional[datetime]

class AvailabilityOut(BaseModel):
    id: UUID
    staff_id: UUID
    start_time: datetime
    end_time: datetime

    class Config:
        orm_mode = True

from pydantic import BaseModel, EmailStr
from uuid import UUID
from typing import Optional
from typing import List

class StaffCreate(BaseModel):
    user_id: UUID
    clinic_id: UUID
    service_ids: List[UUID]

class StaffUpdate(BaseModel):
    service_ids: Optional[List[UUID]]

class StaffOut(BaseModel):
    id: UUID
    user_id: UUID
    clinic_id: UUID
    service_ids: List[UUID]

    class Config:
        orm_mode = True

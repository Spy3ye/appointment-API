from pydantic import BaseModel, EmailStr
from uuid import UUID
from typing import Optional
from datetime import datetime
from enum import Enum
from schemas.User import UserOut
from schemas.Staff import StaffOut
from schemas.Service import ServiceOut
from schemas.Clinic import ClinicOut


class AppStatus(str, Enum):
    booked = "booked"
    completed = "completed"
    canceled = "canceled"

class AppointmentCreate(BaseModel):
    customer_id: UUID
    clinic_id: UUID
    service_id: UUID
    staff_id: UUID
    start_time: datetime
    end_time: datetime

class AppointmentUpdate(BaseModel):
    status: Optional[AppStatus]
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    
class AppointmentDetailedOut(BaseModel):
    id: UUID
    customer: UserOut
    clinic: ClinicOut
    service: ServiceOut
    staff: StaffOut
    start_time: datetime
    end_time: datetime
    status: AppStatus.canceled

class AppointmentOut(BaseModel):
    id: UUID
    customer_id: UUID
    clinic_id: UUID
    service_id: UUID
    staff_id: UUID
    start_time: datetime
    end_time: datetime
    status: AppStatus

    class Config:
        orm_mode = True

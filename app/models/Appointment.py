from pydantic import BaseModel , Field
from typing import Literal
from uuid import UUID , uuid4
from datetime import datetime
from enum import Enum


class AppStatus(str,Enum):
    booked = "booked"
    completed = "completed"
    canceled = "canceled"

class Appointment(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    customer_id: UUID  # User
    clinic_id: UUID
    service_id: UUID
    staff_id: UUID
    start_time: datetime
    end_time: datetime
    status: AppStatus.canceled

from pydantic import BaseModel , Field
from typing import List
from uuid import UUID , uuid4
# from models.User import User
# from models.Clinic import Clinic
# from models.Service import Service


class Staff(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    user_id: UUID
    clinic_id: UUID
    service_ids: List[UUID]  # Services they can provide

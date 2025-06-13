from pydantic import BaseModel , Field
from typing import Optional
from uuid import UUID , uuid4


class Service(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    clinic_id: UUID
    name: str
    description: Optional[str]
    duration_minutes: int
    price: float

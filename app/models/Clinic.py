from pydantic import BaseModel,Field
from typing import Optional
from uuid import UUID , uuid4

class Clinic(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    name: str
    address: str
    phone: str
    description: Optional[str]
    owner_id: UUID  # Link to User (clinic manager)

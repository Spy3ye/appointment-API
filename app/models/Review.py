from pydantic import BaseModel , Field
from typing import Optional
from uuid import UUID , uuid4
from enum import Enum

class ReviewTarget(str, Enum):
    clinic = "clinic"
    staff = "staff"
    service = "service"

class Review(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    target_id: UUID
    target_type: ReviewTarget
    rating: int  # 1–5
    comment: Optional[str]

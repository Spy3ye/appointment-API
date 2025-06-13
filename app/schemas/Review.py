from pydantic import BaseModel, Field, conint
from uuid import UUID
from typing import Optional
from datetime import datetime
from enum import Enum

# LimitReview = conint(ge=18, le=100)

class ReviewTarget(str, Enum):
    clinic = "clinic"
    staff = "staff"
    service = "service"

class ReviewCreate(BaseModel):
    user_id: UUID
    target_id: UUID  # Clinic ID, Staff ID, or Service ID
    target_type: ReviewTarget
    rating: int  # only 1 to 5 allowed
    comment: Optional[str]


class ReviewUpdate(BaseModel):
    rating: Optional[int]
    comment: Optional[str]


class ReviewOut(BaseModel):
    id: UUID
    user_id: UUID
    target_id: UUID
    target_type: ReviewTarget
    rating: int
    comment: Optional[str]
    created_at: datetime

    class Config:
        orm_mode = True

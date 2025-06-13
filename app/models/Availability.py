from pydantic import BaseModel , Field
from typing import Literal
from uuid import UUID , uuid4
from datetime import time

class Availability(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    staff_id: UUID
    weekday: Literal[0, 1, 2, 3, 4, 5, 6]  # friday = 0
    start_time: time
    end_time: time

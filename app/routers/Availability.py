from fastapi import APIRouter, Depends, HTTPException, Query
from uuid import UUID
from datetime import datetime
from typing import List

from services.Availability import get_availability_service
from schemas.Availability import AvailabilityCreate, AvailabilityUpdate, AvailabilityOut

router = APIRouter(prefix="/availabilities", tags=["Availability"])


@router.post("/", response_model=AvailabilityOut, status_code=201)
async def create_availability(availability_data: AvailabilityCreate):
    return await get_availability_service.create_availability(availability_data)


@router.get("/{availability_id}", response_model=AvailabilityOut)
async def get_availability_by_id(availability_id: UUID):
    return await get_availability_service.get_availability_by_id(availability_id)


@router.get("/staff/{staff_id}", response_model=List[AvailabilityOut])
async def get_availability_by_staff(staff_id: UUID):
    return await get_availability_service.get_availability_by_staff(staff_id)


@router.get("/staff/{staff_id}/range", response_model=List[AvailabilityOut])
async def get_availability_by_date_range(
    staff_id: UUID,
    start_date: datetime = Query(..., description="Start date of range"),
    end_date: datetime = Query(..., description="End date of range")
):
    return await get_availability_service.get_availability_by_date_range(staff_id, start_date, end_date)


@router.get("/", response_model=List[AvailabilityOut])
async def get_all_availability(skip: int = 0, limit: int = 100):
    return await get_availability_service.get_all_availability(skip=skip, limit=limit)


@router.put("/{availability_id}", response_model=AvailabilityOut)
async def update_availability(availability_id: UUID, update_data: AvailabilityUpdate):
    return await get_availability_service.update_availability(availability_id, update_data)


@router.delete("/{availability_id}", response_model=bool)
async def delete_availability(availability_id: UUID):
    return await get_availability_service.delete_availability(availability_id)

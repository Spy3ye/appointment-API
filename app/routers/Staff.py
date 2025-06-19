from uuid import UUID
from typing import List, Optional

from fastapi import APIRouter, Query

from schemas.Staff import StaffCreate, StaffUpdate, StaffOut
from services.Staff import get_staff_service

router = APIRouter(prefix="/staff", tags=["Staff"])


@router.post("/", response_model=StaffOut, status_code=201)
async def create_staff(staff_data: StaffCreate):
    return await get_staff_service.create_staff(staff_data)


@router.get("/{staff_id}", response_model=Optional[StaffOut])
async def get_staff_by_id(staff_id: UUID):
    return await get_staff_service.get_staff_by_id(staff_id)


@router.get("/user/{user_id}", response_model=List[StaffOut])
async def get_staff_by_user_id(user_id: UUID):
    return await get_staff_service.get_staff_by_user_id(user_id)


@router.get("/clinic/{clinic_id}", response_model=List[StaffOut])
async def get_staff_by_clinic_id(clinic_id: UUID):
    return await get_staff_service.get_staff_by_clinic_id(clinic_id)


@router.get("/service/{service_id}", response_model=List[StaffOut])
async def get_staff_by_service_id(service_id: UUID):
    return await get_staff_service.get_staff_by_service_id(service_id)


@router.put("/{staff_id}", response_model=Optional[StaffOut])
async def update_staff(staff_id: UUID, staff_update: StaffUpdate):
    return await get_staff_service.update_staff(staff_id, staff_update)


@router.delete("/{staff_id}", response_model=bool)
async def delete_staff(staff_id: UUID):
    return await get_staff_service.delete_staff(staff_id)


@router.get("/", response_model=List[StaffOut])
async def get_all_staff(skip: int = 0, limit: int = 100):
    return await get_staff_service.get_all_staff(skip, limit)

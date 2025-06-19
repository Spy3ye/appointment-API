from uuid import UUID
from typing import List

from fastapi import APIRouter, Query, Depends, HTTPException
from schemas.Clinic import ClinicCreate, ClinicUpdate, ClinicOut
from services.Clinic import get_clinic_service

router = APIRouter(prefix="/clinics", tags=["Clinic"])


@router.post("/", response_model=ClinicOut, status_code=201)
async def create_clinic(clinic_data: ClinicCreate, owner_id: UUID = Query(..., description="Owner user ID")):
    return await get_clinic_service.create_clinic(clinic_data, owner_id)


@router.get("/{clinic_id}", response_model=ClinicOut)
async def get_clinic_by_id(clinic_id: UUID):
    return await get_clinic_service.get_clinic_by_id(clinic_id)


@router.get("/", response_model=List[ClinicOut])
async def get_all_clinics(skip: int = 0, limit: int = 100):
    return await get_clinic_service.get_all_clinics(skip=skip, limit=limit)


@router.get("/owner/{owner_id}", response_model=List[ClinicOut])
async def get_clinics_by_owner(owner_id: UUID):
    return await get_clinic_service.get_clinics_by_owner(owner_id)


@router.get("/search/", response_model=List[ClinicOut])
async def search_clinics(
    search_term: str = Query(..., description="Search by clinic name or address"),
    skip: int = 0,
    limit: int = 100
):
    return await get_clinic_service.search_clinics(search_term, skip, limit)


@router.put("/{clinic_id}", response_model=ClinicOut)
async def update_clinic(clinic_id: UUID, update_data: ClinicUpdate, user_id: UUID = Query(...)):
    return await get_clinic_service.update_clinic(clinic_id, update_data, user_id)


@router.delete("/{clinic_id}", response_model=bool)
async def delete_clinic(clinic_id: UUID, user_id: UUID = Query(...)):
    return await get_clinic_service.delete_clinic(clinic_id, user_id)


@router.get("/{clinic_id}/stats", response_model=dict)
async def get_clinic_stats(clinic_id: UUID):
    return await get_clinic_service.get_clinic_stats(clinic_id)

from uuid import UUID
from typing import List, Optional

from fastapi import APIRouter, Query

from schemas.Service import ServiceCreate, ServiceUpdate, ServiceOut
from services.Service import get_service_service

router = APIRouter(prefix="/services", tags=["Service"])


@router.post("/", response_model=ServiceOut, status_code=201)
async def create_service(
    service_data: ServiceCreate,
    clinic_id: UUID = Query(...),
    user_id: UUID = Query(...)
):
    return await get_service_service.create_service(service_data, clinic_id, user_id)


@router.get("/{service_id}", response_model=ServiceOut)
async def get_service_by_id(service_id: UUID):
    return await get_service_service.get_service_by_id(service_id)


@router.get("/clinic/{clinic_id}", response_model=List[ServiceOut])
async def get_services_by_clinic(clinic_id: UUID, skip: int = 0, limit: int = 100):
    return await get_service_service.get_services_by_clinic(clinic_id, skip, limit)


@router.get("/", response_model=List[ServiceOut])
async def get_all_services(skip: int = 0, limit: int = 100):
    return await get_service_service.get_all_services(skip, limit)


@router.get("/search", response_model=List[ServiceOut])
async def search_services(
    search_term: str,
    clinic_id: Optional[UUID] = None,
    skip: int = 0,
    limit: int = 100
):
    return await get_service_service.search_services(search_term, clinic_id, skip, limit)


@router.get("/price-range", response_model=List[ServiceOut])
async def get_services_by_price_range(
    min_price: float,
    max_price: float,
    clinic_id: Optional[UUID] = None,
    skip: int = 0,
    limit: int = 100
):
    return await get_service_service.get_services_by_price_range(min_price, max_price, clinic_id, skip, limit)


@router.put("/{service_id}", response_model=ServiceOut)
async def update_service(
    service_id: UUID,
    update_data: ServiceUpdate,
    user_id: UUID = Query(...)
):
    return await get_service_service.update_service(service_id, update_data, user_id)


@router.delete("/{service_id}", response_model=bool)
async def delete_service(service_id: UUID, user_id: UUID = Query(...)):
    return await get_service_service.delete_service(service_id, user_id)


@router.get("/stats/{service_id}", response_model=dict)
async def get_service_stats(service_id: UUID):
    return await get_service_service.get_service_stats(service_id)

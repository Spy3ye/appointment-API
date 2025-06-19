from uuid import UUID
from typing import List

from fastapi import APIRouter, Query, Depends
from schemas.Review import ReviewCreate, ReviewUpdate, ReviewOut
from models.Review import ReviewTarget
from services.Review import get_review_service

router = APIRouter(prefix="/reviews", tags=["Review"])


@router.post("/", response_model=ReviewOut, status_code=201)
async def create_review(review_data: ReviewCreate):
    return await get_review_service.create_review(review_data)


@router.get("/{review_id}", response_model=ReviewOut)
async def get_review_by_id(review_id: UUID):
    return await get_review_service.get_review_by_id(review_id)


@router.get("/target/{target_id}", response_model=List[ReviewOut])
async def get_reviews_by_target(
    target_id: UUID,
    target_type: ReviewTarget = Query(...),
    skip: int = 0,
    limit: int = 100
):
    return await get_review_service.get_reviews_by_target(target_id, target_type, skip, limit)


@router.get("/user/{user_id}", response_model=List[ReviewOut])
async def get_reviews_by_user(user_id: UUID, skip: int = 0, limit: int = 100):
    return await get_review_service.get_reviews_by_user(user_id, skip, limit)


@router.put("/{review_id}", response_model=ReviewOut)
async def update_review(review_id: UUID, update_data: ReviewUpdate, user_id: UUID = Query(...)):
    return await get_review_service.update_review(review_id, update_data, user_id)


@router.delete("/{review_id}", response_model=bool)
async def delete_review(review_id: UUID, user_id: UUID = Query(...)):
    return await get_review_service.delete_review(review_id, user_id)


@router.get("/stats/{target_id}", response_model=dict)
async def get_review_statistics(
    target_id: UUID,
    target_type: ReviewTarget = Query(...)
):
    return await get_review_service.get_review_statistics(target_id, target_type)

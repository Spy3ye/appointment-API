from uuid import UUID
from datetime import datetime
from typing import List, Optional
from fastapi import HTTPException
from database.collections import (
    get_review_collection, get_user_collection, get_clinic_collection,
    get_staff_collection, get_service_collection
)
from models.Review import Review, ReviewTarget
from schemas.Review import ReviewCreate, ReviewUpdate, ReviewOut


class ReviewService:
    def __init__(self):
        self.collection = get_review_collection()
        self.user_collection = get_user_collection()
        self.clinic_collection = get_clinic_collection()
        self.staff_collection = get_staff_collection()
        self.service_collection = get_service_collection()

    async def create_review(self, review_data: ReviewCreate) -> ReviewOut:
        """Create a new review"""
        # Validate user exists
        user = await self.user_collection.find_one({"_id": str(review_data.user_id)})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Validate target exists based on target type
        await self._validate_review_target(review_data.target_id, review_data.target_type)
        
        # Validate rating is between 1 and 5
        if not (1 <= review_data.rating <= 5):
            raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
        
        # Check if user has already reviewed this target
        existing_review = await self.collection.find_one({
            "user_id": str(review_data.user_id),
            "target_id": str(review_data.target_id),
            "target_type": review_data.target_type
        })
        if existing_review:
            raise HTTPException(status_code=400, detail="You have already reviewed this item")
        
        review = Review(
            target_id=review_data.target_id,
            target_type=review_data.target_type,
            rating=review_data.rating,
            comment=review_data.comment
        )
        
        review_dict = review.model_dump()
        review_dict["_id"] = str(review.id)
        review_dict["user_id"] = str(review_data.user_id)
        review_dict["created_at"] = datetime.utcnow()
        
        result = await self.collection.insert_one(review_dict)
        if result.inserted_id:
            return ReviewOut(
                id=review.id,
                user_id=review_data.user_id,
                target_id=review.target_id,
                target_type=review.target_type,
                rating=review.rating,
                comment=review.comment,
                created_at=review_dict["created_at"]
            )
        
        raise HTTPException(status_code=500, detail="Failed to create review")

    async def get_review_by_id(self, review_id: UUID) -> ReviewOut:
        """Get review by ID"""
        review = await self.collection.find_one({"_id": str(review_id)})
        if not review:
            raise HTTPException(status_code=404, detail="Review not found")
        
        return ReviewOut(
            id=UUID(review["_id"]),
            user_id=UUID(review["user_id"]),
            target_id=UUID(review["target_id"]),
            target_type=review["target_type"],
            rating=review["rating"],
            comment=review.get("comment"),
            created_at=review["created_at"]
        )

    async def get_reviews_by_target(self, target_id: UUID, target_type: ReviewTarget, skip: int = 0, limit: int = 100) -> List[ReviewOut]:
        """Get all reviews for a specific target"""
        query = {
            "target_id": str(target_id),
            "target_type": target_type
        }
        
        cursor = self.collection.find(query).sort("created_at", -1).skip(skip).limit(limit)
        reviews = await cursor.to_list(length=None)
        
        result = []
        for review in reviews:
            result.append(ReviewOut(
                id=UUID(review["_id"]),
                user_id=UUID(review["user_id"]),
                target_id=UUID(review["target_id"]),
                target_type=review["target_type"],
                rating=review["rating"],
                comment=review.get("comment"),
                created_at=review["created_at"]
            ))
        
        return result

    async def get_reviews_by_user(self, user_id: UUID, skip: int = 0, limit: int = 100) -> List[ReviewOut]:
        """Get all reviews by a specific user"""
        cursor = self.collection.find({"user_id": str(user_id)}).sort("created_at", -1).skip(skip).limit(limit)
        reviews = await cursor.to_list(length=None)
        
        result = []
        for review in reviews:
            result.append(ReviewOut(
                id=UUID(review["_id"]),
                user_id=UUID(review["user_id"]),
                target_id=UUID(review["target_id"]),
                target_type=review["target_type"],
                rating=review["rating"],
                comment=review.get("comment"),
                created_at=review["created_at"]
            ))
        
        return result

    async def update_review(self, review_id: UUID, update_data: ReviewUpdate, user_id: UUID) -> ReviewOut:
        """Update a review"""
        review = await self.collection.find_one({"_id": str(review_id)})
        if not review:
            raise HTTPException(status_code=404, detail="Review not found")
        
        # Check if user owns this review
        if str(review["user_id"]) != str(user_id):
            raise HTTPException(status_code=403, detail="Not authorized to update this review")
        
        update_dict = {}
        if update_data.rating is not None:
            if not (1 <= update_data.rating <= 5):
                raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
            update_dict["rating"] = update_data.rating
            
        if update_data.comment is not None:
            update_dict["comment"] = update_data.comment
        
        if update_dict:
            update_dict["updated_at"] = datetime.utcnow()
            result = await self.collection.update_one(
                {"_id": str(review_id)},
                {"$set": update_dict}
            )
            
            if result.modified_count:
                updated_review = await self.collection.find_one({"_id": str(review_id)})
                return ReviewOut(
                    id=UUID(updated_review["_id"]),
                    user_id=UUID(updated_review["user_id"]),
                    target_id=UUID(updated_review["target_id"]),
                    target_type=updated_review["target_type"],
                    rating=updated_review["rating"],
                    comment=updated_review.get("comment"),
                    created_at=updated_review["created_at"]
                )
        
        raise HTTPException(status_code=500, detail="Failed to update review")

    async def delete_review(self, review_id: UUID, user_id: UUID) -> bool:
        """Delete a review"""
        review = await self.collection.find_one({"_id": str(review_id)})
        if not review:
            raise HTTPException(status_code=404, detail="Review not found")
        
        # Check if user owns this review or is admin
        user = await self.user_collection.find_one({"_id": str(user_id)})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        if str(review["user_id"]) != str(user_id) and user.get("role") != "admin":
            raise HTTPException(status_code=403, detail="Not authorized to delete this review")
        
        result = await self.collection.delete_one({"_id": str(review_id)})
        if result.deleted_count:
            return True
        
        raise HTTPException(status_code=500, detail="Failed to delete review")

    async def get_review_statistics(self, target_id: UUID, target_type: ReviewTarget) -> dict:
        """Get review statistics for a target"""
        pipeline = [
            {
                "$match": {
                    "target_id": str(target_id),
                    "target_type": target_type
                }
            },
            {
                "$group": {
                    "_id": None,
                    "total_reviews": {"$sum": 1},
                    "average_rating": {"$avg": "$rating"},
                    "rating_distribution": {
                        "$push": "$rating"
                    }
                }
            }
        ]
        
        result = await self.collection.aggregate(pipeline).to_list(length=1)
        
        if not result:
            return {
                "target_id": str(target_id),
                "target_type": target_type,
                "total_reviews": 0,
                "average_rating": 0,
                "rating_distribution": {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
            }
        
        stats = result[0]
        
        # Calculate rating distribution
        rating_dist = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        for rating in stats["rating_distribution"]:
            rating_dist[rating] += 1
        
        return {
            "target_id": str(target_id),
            "target_type": target_type,
            "total_reviews": stats["total_reviews"],
            "average_rating": round(stats["average_rating"], 2) if stats["average_rating"] else 0,
            "rating_distribution": rating_dist
        }

    async def _validate_review_target(self, target_id: UUID, target_type: ReviewTarget):
        """Validate that the review target exists"""
        if target_type == ReviewTarget.clinic:
            target = await self.clinic_collection.find_one({"_id": str(target_id)})
            if not target:
                raise HTTPException(status_code=404, detail="Clinic not found")
        
        elif target_type == ReviewTarget.staff:
            target = await self.staff_collection.find_one({"_id": str(target_id)})
            if not target:
                raise HTTPException(status_code=404, detail="Staff not found")
        
        elif target_type == ReviewTarget.service:
            target = await self.service_collection.find_one({"_id": str(target_id)})
            if not target:
                raise HTTPException(status_code=404, detail="Service not found")
        
        else:
            raise HTTPException(status_code=400, detail="Invalid target type")


# Create a global instance
# review_service = ReviewService()

def get_review_service() -> ReviewService:
    return ReviewService()
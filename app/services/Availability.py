from uuid import UUID
from datetime import datetime
from typing import List, Optional
from fastapi import HTTPException
from database.collections import get_availability_collection, get_staff_collection
from models.Availability import Availability
from schemas.Availability import AvailabilityCreate, AvailabilityUpdate, AvailabilityOut



class AvailabilityService:
    def __init__(self):
        self.collection = get_availability_collection()
        self.staff_collection = get_staff_collection()

    async def create_availability(db, availability_data: AvailabilityCreate) -> AvailabilityOut:
        """Create a new availability slot"""
        # Validate that staff exists
        staff = await db["staff"].staff_collection.find_one({"_id": str(availability_data.staff_id)})
        if not staff:
            raise HTTPException(status_code=404, detail="Staff not found")
        
        # Check for overlapping availability slots
        await self._check_availability_conflicts(availability_data)
        
        availability = Availability(
            staff_id=availability_data.staff_id,
            weekday=availability_data.start_time.weekday(),  # Calculate weekday from start_time
            start_time=availability_data.start_time.time(),
            end_time=availability_data.end_time.time()
        )
        
        availability_dict = availability.model_dump()
        availability_dict["_id"] = str(availability.id)
        # Convert time objects to strings for MongoDB storage
        availability_dict["start_time"] = availability_data.start_time
        availability_dict["end_time"] = availability_data.end_time
        
        result = await self.collection.insert_one(availability_dict)
        if result.inserted_id:
            return AvailabilityOut(
                id=availability.id,
                staff_id=availability_data.staff_id,
                start_time=availability_data.start_time,
                end_time=availability_data.end_time
            )
        
        raise HTTPException(status_code=500, detail="Failed to create availability")

    async def get_availability_by_id(self, availability_id: UUID) -> AvailabilityOut:
        """Get availability by ID"""
        availability = await self.collection.find_one({"_id": str(availability_id)})
        if not availability:
            raise HTTPException(status_code=404, detail="Availability not found")
        
        return AvailabilityOut(
            id=UUID(availability["_id"]),
            staff_id=UUID(availability["staff_id"]),
            start_time=availability["start_time"],
            end_time=availability["end_time"]
        )

    async def get_availability_by_staff(self, staff_id: UUID) -> List[AvailabilityOut]:
        """Get all availability slots for a staff member"""
        cursor = self.collection.find({"staff_id": str(staff_id)})
        availabilities = await cursor.to_list(length=None)
        
        result = []
        for availability in availabilities:
            result.append(AvailabilityOut(
                id=UUID(availability["_id"]),
                staff_id=UUID(availability["staff_id"]),
                start_time=availability["start_time"],
                end_time=availability["end_time"]
            ))
        
        return result

    async def get_availability_by_date_range(self, staff_id: UUID, start_date: datetime, end_date: datetime) -> List[AvailabilityOut]:
        """Get availability slots for a staff member within a date range"""
        query = {
            "staff_id": str(staff_id),
            "start_time": {"$gte": start_date, "$lte": end_date}
        }
        
        cursor = self.collection.find(query)
        availabilities = await cursor.to_list(length=None)
        
        result = []
        for availability in availabilities:
            result.append(AvailabilityOut(
                id=UUID(availability["_id"]),
                staff_id=UUID(availability["staff_id"]),
                start_time=availability["start_time"],
                end_time=availability["end_time"]
            ))
        
        return result

    async def update_availability(self, availability_id: UUID, update_data: AvailabilityUpdate) -> AvailabilityOut:
        """Update an availability slot"""
        availability = await self.collection.find_one({"_id": str(availability_id)})
        if not availability:
            raise HTTPException(status_code=404, detail="Availability not found")
        
        update_dict = {}
        if update_data.start_time is not None:
            update_dict["start_time"] = update_data.start_time
        if update_data.end_time is not None:
            update_dict["end_time"] = update_data.end_time
        
        if update_dict:
            # Check for conflicts with the updated times
            temp_availability = AvailabilityCreate(
                staff_id=UUID(availability["staff_id"]),
                start_time=update_dict.get("start_time", availability["start_time"]),
                end_time=update_dict.get("end_time", availability["end_time"])
            )
            await self._check_availability_conflicts(temp_availability, exclude_availability_id=availability_id)
            
            result = await self.collection.update_one(
                {"_id": str(availability_id)},
                {"$set": update_dict}
            )
            
            if result.modified_count:
                updated_availability = await self.collection.find_one({"_id": str(availability_id)})
                return AvailabilityOut(
                    id=UUID(updated_availability["_id"]),
                    staff_id=UUID(updated_availability["staff_id"]),
                    start_time=updated_availability["start_time"],
                    end_time=updated_availability["end_time"]
                )
        
        raise HTTPException(status_code=500, detail="Failed to update availability")

    async def delete_availability(self, availability_id: UUID) -> bool:
        """Delete an availability slot"""
        result = await self.collection.delete_one({"_id": str(availability_id)})
        if result.deleted_count:
            return True
        raise HTTPException(status_code=404, detail="Availability not found")

    async def get_all_availability(self, skip: int = 0, limit: int = 100) -> List[AvailabilityOut]:
        """Get all availability slots with pagination"""
        cursor = self.collection.find({}).skip(skip).limit(limit)
        availabilities = await cursor.to_list(length=None)
        
        result = []
        for availability in availabilities:
            result.append(AvailabilityOut(
                id=UUID(availability["_id"]),
                staff_id=UUID(availability["staff_id"]),
                start_time=availability["start_time"],
                end_time=availability["end_time"]
            ))
        
        return result

    async def _check_availability_conflicts(self, availability_data: AvailabilityCreate, exclude_availability_id: Optional[UUID] = None):
        """Check for overlapping availability slots for the same staff member"""
        query = {
            "staff_id": str(availability_data.staff_id),
            "$or": [
                {
                    "start_time": {"$lte": availability_data.start_time},
                    "end_time": {"$gt": availability_data.start_time}
                },
                {
                    "start_time": {"$lt": availability_data.end_time},
                    "end_time": {"$gte": availability_data.end_time}
                },
                {
                    "start_time": {"$gte": availability_data.start_time},
                    "end_time": {"$lte": availability_data.end_time}
                }
            ]
        }
        
        # Exclude current availability if updating
        if exclude_availability_id:
            query["_id"] = {"$ne": str(exclude_availability_id)}
        
        conflict = await self.collection.find_one(query)
        if conflict:
            raise HTTPException(status_code=400, detail="Availability slot conflicts with existing slot")


# Create a global instance
# availability_service = AvailabilityService()
def get_availability_service() -> AvailabilityService:
    return AvailabilityService()
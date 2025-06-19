from bson import ObjectId
from uuid import UUID
from typing import List, Optional
from fastapi import HTTPException
from database.collections import get_staff_collection, get_user_collection, get_service_collection
from schemas.Staff import StaffCreate, StaffUpdate, StaffOut
from models.Staff import Staff


class StaffService:
    def __init__(self):
        self.collection = get_staff_collection()
        self.user_collection = get_user_collection()
        self.service_collection = get_service_collection()

    async def create_staff(self, staff_data: StaffCreate) -> StaffOut:
        """Create a new staff member"""
        # Verify user exists
        user = await self.user_collection.find_one({"_id": ObjectId(str(staff_data.user_id))})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Verify services exist
        for service_id in staff_data.service_ids:
            service = await self.service_collection.find_one({"_id": ObjectId(str(service_id))})
            if not service:
                raise HTTPException(status_code=404, detail=f"Service {service_id} not found")
        
        # Check if staff already exists for this user and clinic
        existing_staff = await self.collection.find_one({
            "user_id": str(staff_data.user_id),
            "clinic_id": str(staff_data.clinic_id)
        })
        if existing_staff:
            raise HTTPException(status_code=400, detail="Staff member already exists for this user and clinic")
        
        # Create staff
        staff = Staff(**staff_data.dict())
        staff_dict = staff.dict()
        staff_dict["_id"] = ObjectId()
        staff_dict["id"] = str(staff_dict["_id"])
        staff_dict["user_id"] = str(staff_dict["user_id"])
        staff_dict["clinic_id"] = str(staff_dict["clinic_id"])
        staff_dict["service_ids"] = [str(sid) for sid in staff_dict["service_ids"]]
        
        result = await self.collection.insert_one(staff_dict)
        
        # Retrieve the created staff
        created_staff = await self.collection.find_one({"_id": result.inserted_id})
        created_staff["id"] = str(created_staff["_id"])
        
        return StaffOut(**created_staff)

    async def get_staff_by_id(self, staff_id: UUID) -> Optional[StaffOut]:
        """Get staff by ID"""
        staff = await self.collection.find_one({"_id": ObjectId(str(staff_id))})
        if not staff:
            return None
        
        staff["id"] = str(staff["_id"])
        return StaffOut(**staff)

    async def get_staff_by_user_id(self, user_id: UUID) -> List[StaffOut]:
        """Get all staff records for a user"""
        cursor = self.collection.find({"user_id": str(user_id)})
        staff_list = []
        
        async for staff in cursor:
            staff["id"] = str(staff["_id"])
            staff_list.append(StaffOut(**staff))
        
        return staff_list

    async def get_staff_by_clinic_id(self, clinic_id: UUID) -> List[StaffOut]:
        """Get all staff for a clinic"""
        cursor = self.collection.find({"clinic_id": str(clinic_id)})
        staff_list = []
        
        async for staff in cursor:
            staff["id"] = str(staff["_id"])
            staff_list.append(StaffOut(**staff))
        
        return staff_list

    async def get_staff_by_service_id(self, service_id: UUID) -> List[StaffOut]:
        """Get all staff who can provide a specific service"""
        cursor = self.collection.find({"service_ids": str(service_id)})
        staff_list = []
        
        async for staff in cursor:
            staff["id"] = str(staff["_id"])
            staff_list.append(StaffOut(**staff))
        
        return staff_list

    async def update_staff(self, staff_id: UUID, staff_update: StaffUpdate) -> Optional[StaffOut]:
        """Update staff information"""
        update_data = staff_update.dict(exclude_unset=True)
        
        # Verify services exist if updating service_ids
        if "service_ids" in update_data:
            for service_id in update_data["service_ids"]:
                service = await self.service_collection.find_one({"_id": ObjectId(str(service_id))})
                if not service:
                    raise HTTPException(status_code=404, detail=f"Service {service_id} not found")
            update_data["service_ids"] = [str(sid) for sid in update_data["service_ids"]]
        
        if not update_data:
            # No updates provided
            return await self.get_staff_by_id(staff_id)
        
        result = await self.collection.update_one(
            {"_id": ObjectId(str(staff_id))},
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            return None
        
        return await self.get_staff_by_id(staff_id)

    async def delete_staff(self, staff_id: UUID) -> bool:
        """Delete staff member"""
        result = await self.collection.delete_one({"_id": ObjectId(str(staff_id))})
        return result.deleted_count > 0

    async def get_all_staff(self, skip: int = 0, limit: int = 100) -> List[StaffOut]:
        """Get all staff with pagination"""
        cursor = self.collection.find().skip(skip).limit(limit)
        staff_list = []
        
        async for staff in cursor:
            staff["id"] = str(staff["_id"])
            staff_list.append(StaffOut(**staff))
        
        return staff_list


# Create service instance
# staff_service = StaffService()

def get_staff_service() -> StaffService:
    return StaffService()
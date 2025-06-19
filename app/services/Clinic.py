from uuid import UUID
from typing import List, Optional
from fastapi import HTTPException
from database.collections import get_clinic_collection, get_user_collection
from models.Clinic import Clinic
from schemas.Clinic import ClinicCreate, ClinicUpdate, ClinicOut


class ClinicService:
    def __init__(self):
        self.collection = get_clinic_collection()
        self.user_collection = get_user_collection()

    async def create_clinic(self, clinic_data: ClinicCreate, owner_id: UUID) -> ClinicOut:
        """Create a new clinic"""
        # Validate that owner exists and has appropriate role
        owner = await self.user_collection.find_one({"_id": str(owner_id)})
        if not owner:
            raise HTTPException(status_code=404, detail="Owner not found")
        
        # Check if owner role is appropriate (clinic_manager or admin)
        if owner.get("role") not in ["clinic_manager", "admin"]:
            raise HTTPException(status_code=403, detail="User does not have permission to create a clinic")
        
        # Check if clinic name already exists
        existing_clinic = await self.collection.find_one({"name": clinic_data.name})
        if existing_clinic:
            raise HTTPException(status_code=400, detail="Clinic with this name already exists")
        
        clinic = Clinic(
            name=clinic_data.name,
            address=clinic_data.address,
            phone=clinic_data.phone or "",
            description="",
            owner_id=owner_id
        )
        
        clinic_dict = clinic.model_dump()
        clinic_dict["_id"] = str(clinic.id)
        
        result = await self.collection.insert_one(clinic_dict)
        if result.inserted_id:
            return ClinicOut(
                id=clinic.id,
                name=clinic.name,
                address=clinic.address,
                phone=clinic.phone
            )
        
        raise HTTPException(status_code=500, detail="Failed to create clinic")

    async def get_clinic_by_id(self, clinic_id: UUID) -> ClinicOut:
        """Get clinic by ID"""
        clinic = await self.collection.find_one({"_id": str(clinic_id)})
        if not clinic:
            raise HTTPException(status_code=404, detail="Clinic not found")
        
        return ClinicOut(
            id=UUID(clinic["_id"]),
            name=clinic["name"],
            address=clinic["address"],
            phone=clinic.get("phone")
        )

    async def get_all_clinics(self, skip: int = 0, limit: int = 100) -> List[ClinicOut]:
        """Get all clinics with pagination"""
        cursor = self.collection.find({}).skip(skip).limit(limit)
        clinics = await cursor.to_list(length=None)
        
        result = []
        for clinic in clinics:
            result.append(ClinicOut(
                id=UUID(clinic["_id"]),
                name=clinic["name"],
                address=clinic["address"],
                phone=clinic.get("phone")
            ))
        
        return result

    async def get_clinics_by_owner(self, owner_id: UUID) -> List[ClinicOut]:
        """Get all clinics owned by a specific user"""
        cursor = self.collection.find({"owner_id": str(owner_id)})
        clinics = await cursor.to_list(length=None)
        
        result = []
        for clinic in clinics:
            result.append(ClinicOut(
                id=UUID(clinic["_id"]),
                name=clinic["name"],
                address=clinic["address"],
                phone=clinic.get("phone")
            ))
        
        return result

    async def search_clinics(self, search_term: str, skip: int = 0, limit: int = 100) -> List[ClinicOut]:
        """Search clinics by name or address"""
        query = {
            "$or": [
                {"name": {"$regex": search_term, "$options": "i"}},
                {"address": {"$regex": search_term, "$options": "i"}}
            ]
        }
        
        cursor = self.collection.find(query).skip(skip).limit(limit)
        clinics = await cursor.to_list(length=None)
        
        result = []
        for clinic in clinics:
            result.append(ClinicOut(
                id=UUID(clinic["_id"]),
                name=clinic["name"],
                address=clinic["address"],
                phone=clinic.get("phone")
            ))
        
        return result

    async def update_clinic(self, clinic_id: UUID, update_data: ClinicUpdate, user_id: UUID) -> ClinicOut:
        """Update a clinic"""
        clinic = await self.collection.find_one({"_id": str(clinic_id)})
        if not clinic:
            raise HTTPException(status_code=404, detail="Clinic not found")
        
        # Check if user has permission to update this clinic
        user = await self.user_collection.find_one({"_id": str(user_id)})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Only owner or admin can update
        if str(clinic["owner_id"]) != str(user_id) and user.get("role") != "admin":
            raise HTTPException(status_code=403, detail="Not authorized to update this clinic")
        
        update_dict = {}
        if update_data.name is not None:
            # Check if new name already exists (excluding current clinic)
            existing_clinic = await self.collection.find_one({
                "name": update_data.name,
                "_id": {"$ne": str(clinic_id)}
            })
            if existing_clinic:
                raise HTTPException(status_code=400, detail="Clinic with this name already exists")
            update_dict["name"] = update_data.name
            
        if update_data.address is not None:
            update_dict["address"] = update_data.address
            
        if update_data.phone is not None:
            update_dict["phone"] = update_data.phone
        
        if update_dict:
            result = await self.collection.update_one(
                {"_id": str(clinic_id)},
                {"$set": update_dict}
            )
            
            if result.modified_count:
                updated_clinic = await self.collection.find_one({"_id": str(clinic_id)})
                return ClinicOut(
                    id=UUID(updated_clinic["_id"]),
                    name=updated_clinic["name"],
                    address=updated_clinic["address"],
                    phone=updated_clinic.get("phone")
                )
        
        raise HTTPException(status_code=500, detail="Failed to update clinic")

    async def delete_clinic(self, clinic_id: UUID, user_id: UUID) -> bool:
        """Delete a clinic"""
        clinic = await self.collection.find_one({"_id": str(clinic_id)})
        if not clinic:
            raise HTTPException(status_code=404, detail="Clinic not found")
        
        # Check if user has permission to delete this clinic
        user = await self.user_collection.find_one({"_id": str(user_id)})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Only owner or admin can delete
        if str(clinic["owner_id"]) != str(user_id) and user.get("role") != "admin":
            raise HTTPException(status_code=403, detail="Not authorized to delete this clinic")
        
        result = await self.collection.delete_one({"_id": str(clinic_id)})
        if result.deleted_count:
            return True
        
        raise HTTPException(status_code=500, detail="Failed to delete clinic")

    async def get_clinic_stats(self, clinic_id: UUID) -> dict:
        """Get basic statistics for a clinic"""
        clinic = await self.collection.find_one({"_id": str(clinic_id)})
        if not clinic:
            raise HTTPException(status_code=404, detail="Clinic not found")
        
        # Import here to avoid circular imports
        from database.collections import get_staff_collection, get_service_collection, get_appointment_collection
        
        staff_collection = get_staff_collection()
        service_collection = get_service_collection()
        appointment_collection = get_appointment_collection()
        
        # Count staff members
        staff_count = await staff_collection.count_documents({"clinic_id": str(clinic_id)})
        
        # Count services
        service_count = await service_collection.count_documents({"clinic_id": str(clinic_id)})
        
        # Count appointments
        appointment_count = await appointment_collection.count_documents({"clinic_id": str(clinic_id)})
        
        return {
            "clinic_id": str(clinic_id),
            "clinic_name": clinic["name"],
            "staff_count": staff_count,
            "service_count": service_count,
            "total_appointments": appointment_count
        }


# Create a global instance
# clinic_service = ClinicService()

def get_clinic_service() -> ClinicService:
    return ClinicService()
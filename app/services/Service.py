from uuid import UUID
from typing import List, Optional
from fastapi import HTTPException
from database.collections import get_service_collection, get_clinic_collection, get_user_collection
from models.Service import Service
from schemas.Service import ServiceCreate, ServiceUpdate, ServiceOut


class ServiceService:
    def __init__(self):
        self.collection = get_service_collection()
        self.clinic_collection = get_clinic_collection()
        self.user_collection = get_user_collection()

    async def create_service(self, service_data: ServiceCreate, clinic_id: UUID, user_id: UUID) -> ServiceOut:
        """Create a new service"""
        # Validate that clinic exists
        clinic = await self.clinic_collection.find_one({"_id": str(clinic_id)})
        if not clinic:
            raise HTTPException(status_code=404, detail="Clinic not found")
        
        # Check if user has permission to create service for this clinic
        user = await self.user_collection.find_one({"_id": str(user_id)})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Only clinic owner or admin can create services
        if str(clinic["owner_id"]) != str(user_id) and user.get("role") != "admin":
            raise HTTPException(status_code=403, detail="Not authorized to create services for this clinic")
        
        # Check if service name already exists in this clinic
        existing_service = await self.collection.find_one({
            "clinic_id": str(clinic_id),
            "name": service_data.name
        })
        if existing_service:
            raise HTTPException(status_code=400, detail="Service with this name already exists in this clinic")
        
        # Validate service data
        if service_data.duration_minutes <= 0:
            raise HTTPException(status_code=400, detail="Duration must be greater than 0")
        
        if service_data.price < 0:
            raise HTTPException(status_code=400, detail="Price cannot be negative")
        
        service = Service(
            clinic_id=clinic_id,
            name=service_data.name,
            description="",
            duration_minutes=service_data.duration_minutes,
            price=service_data.price
        )
        
        service_dict = service.model_dump()
        service_dict["_id"] = str(service.id)
        
        result = await self.collection.insert_one(service_dict)
        if result.inserted_id:
            return ServiceOut(
                id=service.id,
                name=service.name,
                duration_minutes=service.duration_minutes,
                price=service.price
            )
        
        raise HTTPException(status_code=500, detail="Failed to create service")

    async def get_service_by_id(self, service_id: UUID) -> ServiceOut:
        """Get service by ID"""
        service = await self.collection.find_one({"_id": str(service_id)})
        if not service:
            raise HTTPException(status_code=404, detail="Service not found")
        
        return ServiceOut(
            id=UUID(service["_id"]),
            name=service["name"],
            duration_minutes=service["duration_minutes"],
            price=service["price"]
        )

    async def get_services_by_clinic(self, clinic_id: UUID, skip: int = 0, limit: int = 100) -> List[ServiceOut]:
        """Get all services for a specific clinic"""
        # Validate that clinic exists
        clinic = await self.clinic_collection.find_one({"_id": str(clinic_id)})
        if not clinic:
            raise HTTPException(status_code=404, detail="Clinic not found")
        
        cursor = self.collection.find({"clinic_id": str(clinic_id)}).skip(skip).limit(limit)
        services = await cursor.to_list(length=None)
        
        result = []
        for service in services:
            result.append(ServiceOut(
                id=UUID(service["_id"]),
                name=service["name"],
                duration_minutes=service["duration_minutes"],
                price=service["price"]
            ))
        
        return result

    async def get_all_services(self, skip: int = 0, limit: int = 100) -> List[ServiceOut]:
        """Get all services with pagination"""
        cursor = self.collection.find({}).skip(skip).limit(limit)
        services = await cursor.to_list(length=None)
        
        result = []
        for service in services:
            result.append(ServiceOut(
                id=UUID(service["_id"]),
                name=service["name"],
                duration_minutes=service["duration_minutes"],
                price=service["price"]
            ))
        
        return result

    async def search_services(self, search_term: str, clinic_id: Optional[UUID] = None, skip: int = 0, limit: int = 100) -> List[ServiceOut]:
        """Search services by name"""
        query = {
            "name": {"$regex": search_term, "$options": "i"}
        }
        
        if clinic_id:
            query["clinic_id"] = str(clinic_id)
        
        cursor = self.collection.find(query).skip(skip).limit(limit)
        services = await cursor.to_list(length=None)
        
        result = []
        for service in services:
            result.append(ServiceOut(
                id=UUID(service["_id"]),
                name=service["name"],
                duration_minutes=service["duration_minutes"],
                price=service["price"]
            ))
        
        return result

    async def get_services_by_price_range(self, min_price: float, max_price: float, clinic_id: Optional[UUID] = None, skip: int = 0, limit: int = 100) -> List[ServiceOut]:
        """Get services within a price range"""
        query = {
            "price": {"$gte": min_price, "$lte": max_price}
        }
        
        if clinic_id:
            query["clinic_id"] = str(clinic_id)
        
        cursor = self.collection.find(query).skip(skip).limit(limit)
        services = await cursor.to_list(length=None)
        
        result = []
        for service in services:
            result.append(ServiceOut(
                id=UUID(service["_id"]),
                name=service["name"],
                duration_minutes=service["duration_minutes"],
                price=service["price"]
            ))
        
        return result

    async def update_service(self, service_id: UUID, update_data: ServiceUpdate, user_id: UUID) -> ServiceOut:
        """Update a service"""
        service = await self.collection.find_one({"_id": str(service_id)})
        if not service:
            raise HTTPException(status_code=404, detail="Service not found")
        
        # Get the clinic to check permissions
        clinic = await self.clinic_collection.find_one({"_id": service["clinic_id"]})
        if not clinic:
            raise HTTPException(status_code=404, detail="Associated clinic not found")
        
        # Check if user has permission to update this service
        user = await self.user_collection.find_one({"_id": str(user_id)})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Only clinic owner or admin can update services
        if str(clinic["owner_id"]) != str(user_id) and user.get("role") != "admin":
            raise HTTPException(status_code=403, detail="Not authorized to update this service")
        
        update_dict = {}
        
        if update_data.name is not None:
            # Check if new name already exists in this clinic (excluding current service)
            existing_service = await self.collection.find_one({
                "clinic_id": service["clinic_id"],
                "name": update_data.name,
                "_id": {"$ne": str(service_id)}
            })
            if existing_service:
                raise HTTPException(status_code=400, detail="Service with this name already exists in this clinic")
            update_dict["name"] = update_data.name
            
        if update_data.duration_minutes is not None:
            if update_data.duration_minutes <= 0:
                raise HTTPException(status_code=400, detail="Duration must be greater than 0")
            update_dict["duration_minutes"] = update_data.duration_minutes
            
        if update_data.price is not None:
            if update_data.price < 0:
                raise HTTPException(status_code=400, detail="Price cannot be negative")
            update_dict["price"] = update_data.price
        
        if update_dict:
            result = await self.collection.update_one(
                {"_id": str(service_id)},
                {"$set": update_dict}
            )
            
            if result.modified_count:
                updated_service = await self.collection.find_one({"_id": str(service_id)})
                return ServiceOut(
                    id=UUID(updated_service["_id"]),
                    name=updated_service["name"],
                    duration_minutes=updated_service["duration_minutes"],
                    price=updated_service["price"]
                )
        
        raise HTTPException(status_code=500, detail="Failed to update service")

    async def delete_service(self, service_id: UUID, user_id: UUID) -> bool:
        """Delete a service"""
        service = await self.collection.find_one({"_id": str(service_id)})
        if not service:
            raise HTTPException(status_code=404, detail="Service not found")
        
        # Get the clinic to check permissions
        clinic = await self.clinic_collection.find_one({"_id": service["clinic_id"]})
        if not clinic:
            raise HTTPException(status_code=404, detail="Associated clinic not found")
        
        # Check if user has permission to delete this service
        user = await self.user_collection.find_one({"_id": str(user_id)})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Only clinic owner or admin can delete services
        if str(clinic["owner_id"]) != str(user_id) and user.get("role") != "admin":
            raise HTTPException(status_code=403, detail="Not authorized to delete this service")
        
        # Check if service is being used in any appointments or staff assignments
        from database.collections import get_appointment_collection, get_staff_collection
        
        appointment_collection = get_appointment_collection()
        staff_collection = get_staff_collection()
        
        # Check for existing appointments
        appointment_count = await appointment_collection.count_documents({
            "service_id": str(service_id),
            "status": {"$ne": "canceled"}
        })
        
        if appointment_count > 0:
            raise HTTPException(status_code=400, detail="Cannot delete service with active appointments")
        
        # Remove service from staff service lists
        await staff_collection.update_many(
            {"service_ids": str(service_id)},
            {"$pull": {"service_ids": str(service_id)}}
        )
        
        result = await self.collection.delete_one({"_id": str(service_id)})
        if result.deleted_count:
            return True
        
        raise HTTPException(status_code=500, detail="Failed to delete service")

    async def get_service_stats(self, service_id: UUID) -> dict:
        """Get basic statistics for a service"""
        service = await self.collection.find_one({"_id": str(service_id)})
        if not service:
            raise HTTPException(status_code=404, detail="Service not found")
        
        # Import here to avoid circular imports
        from database.collections import get_appointment_collection, get_staff_collection
        
        appointment_collection = get_appointment_collection()
        staff_collection = get_staff_collection()
        
        # Count appointments for this service
        total_appointments = await appointment_collection.count_documents({"service_id": str(service_id)})
        completed_appointments = await appointment_collection.count_documents({
            "service_id": str(service_id),
            "status": "completed"
        })
        
        # Count staff who can provide this service
        staff_count = await staff_collection.count_documents({"service_ids": str(service_id)})
        
        return {
            "service_id": str(service_id),
            "service_name": service["name"],
            "total_appointments": total_appointments,
            "completed_appointments": completed_appointments,
            "staff_count": staff_count,
            "price": service["price"],
            "duration_minutes": service["duration_minutes"]
        }


# Create a global instance
# service_service = ServiceService()

def get_service_service() -> ServiceService:
    return ServiceService()
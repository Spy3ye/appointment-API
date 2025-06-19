from uuid import UUID
from datetime import datetime
from typing import List, Optional
from fastapi import HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase
from database.collections import get_appointment_collection, get_user_collection, get_clinic_collection, get_service_collection, get_staff_collection
from models.Appointment import Appointment, AppStatus
from schemas.Appointment import AppointmentCreate, AppointmentUpdate, AppointmentOut, AppointmentDetailedOut
from schemas.User import UserOut
from schemas.Clinic import ClinicOut
from schemas.Service import ServiceOut
from schemas.Staff import StaffOut


class AppointmentService:
    def __init__(self):
        self.collection = get_appointment_collection()
        self.user_collection = get_user_collection()
        self.clinic_collection = get_clinic_collection()
        self.service_collection = get_service_collection()
        self.staff_collection = get_staff_collection()

    async def create_appointment(self, appointment_data: AppointmentCreate) -> AppointmentOut:
        """Create a new appointment"""
        # Validate that all referenced entities exist
        await self._validate_appointment_references(appointment_data)
        
        # Check for scheduling conflicts
        await self._check_scheduling_conflicts(appointment_data)
        
        appointment = Appointment(
            customer_id=appointment_data.customer_id,
            clinic_id=appointment_data.clinic_id,
            service_id=appointment_data.service_id,
            staff_id=appointment_data.staff_id,
            start_time=appointment_data.start_time,
            end_time=appointment_data.end_time,
            status=AppStatus.booked
        )
        
        appointment_dict = appointment.model_dump()
        appointment_dict["_id"] = str(appointment.id)
        
        result = await self.collection.insert_one(appointment_dict)
        if result.inserted_id:
            return AppointmentOut(**appointment_dict)
        
        raise HTTPException(status_code=500, detail="Failed to create appointment")

    async def get_appointment_by_id(self, appointment_id: UUID) -> AppointmentOut:
        """Get appointment by ID"""
        appointment = await self.collection.find_one({"_id": str(appointment_id)})
        if not appointment:
            raise HTTPException(status_code=404, detail="Appointment not found")
        
        appointment["id"] = appointment["_id"]
        return AppointmentOut(**appointment)

    async def get_detailed_appointment_by_id(self, appointment_id: UUID) -> AppointmentDetailedOut:
        """Get detailed appointment with related data"""
        appointment = await self.collection.find_one({"_id": str(appointment_id)})
        if not appointment:
            raise HTTPException(status_code=404, detail="Appointment not found")
        
        # Fetch related data
        customer = await self.user_collection.find_one({"_id": str(appointment["customer_id"])})
        clinic = await self.clinic_collection.find_one({"_id": str(appointment["clinic_id"])})
        service = await self.service_collection.find_one({"_id": str(appointment["service_id"])})
        staff = await self.staff_collection.find_one({"_id": str(appointment["staff_id"])})
        
        if not all([customer, clinic, service, staff]):
            raise HTTPException(status_code=500, detail="Failed to fetch related appointment data")
        
        # Convert to output schemas
        customer["id"] = customer["_id"]
        clinic["id"] = clinic["_id"]
        service["id"] = service["_id"]
        staff["id"] = staff["_id"]
        
        return AppointmentDetailedOut(
            id=appointment["_id"],
            customer=UserOut(**customer),
            clinic=ClinicOut(**clinic),
            service=ServiceOut(**service),
            staff=StaffOut(**staff),
            start_time=appointment["start_time"],
            end_time=appointment["end_time"],
            status=appointment["status"]
        )

    async def get_appointments_by_customer(self, customer_id: UUID) -> List[AppointmentOut]:
        """Get all appointments for a customer"""
        cursor = self.collection.find({"customer_id": str(customer_id)})
        appointments = await cursor.to_list(length=None)
        
        result = []
        for appointment in appointments:
            appointment["id"] = appointment["_id"]
            result.append(AppointmentOut(**appointment))
        
        return result

    async def get_appointments_by_staff(self, staff_id: UUID) -> List[AppointmentOut]:
        """Get all appointments for a staff member"""
        cursor = self.collection.find({"staff_id": str(staff_id)})
        appointments = await cursor.to_list(length=None)
        
        result = []
        for appointment in appointments:
            appointment["id"] = appointment["_id"]
            result.append(AppointmentOut(**appointment))
        
        return result

    async def get_appointments_by_clinic(self, clinic_id: UUID) -> List[AppointmentOut]:
        """Get all appointments for a clinic"""
        cursor = self.collection.find({"clinic_id": str(clinic_id)})
        appointments = await cursor.to_list(length=None)
        
        result = []
        for appointment in appointments:
            appointment["id"] = appointment["_id"]
            result.append(AppointmentOut(**appointment))
        
        return result

    async def update_appointment(self, appointment_id: UUID, update_data: AppointmentUpdate) -> AppointmentOut:
        """Update an appointment"""
        appointment = await self.collection.find_one({"_id": str(appointment_id)})
        if not appointment:
            raise HTTPException(status_code=404, detail="Appointment not found")
        
        update_dict = {}
        if update_data.status is not None:
            update_dict["status"] = update_data.status
        if update_data.start_time is not None:
            update_dict["start_time"] = update_data.start_time
        if update_data.end_time is not None:
            update_dict["end_time"] = update_data.end_time
        
        if update_dict:
            # Check for scheduling conflicts if time is being updated
            if "start_time" in update_dict or "end_time" in update_dict:
                # Create a temporary appointment object for conflict checking
                temp_appointment = AppointmentCreate(
                    customer_id=UUID(appointment["customer_id"]),
                    clinic_id=UUID(appointment["clinic_id"]),
                    service_id=UUID(appointment["service_id"]),
                    staff_id=UUID(appointment["staff_id"]),
                    start_time=update_dict.get("start_time", appointment["start_time"]),
                    end_time=update_dict.get("end_time", appointment["end_time"])
                )
                await self._check_scheduling_conflicts(temp_appointment, exclude_appointment_id=appointment_id)
            
            result = await self.collection.update_one(
                {"_id": str(appointment_id)},
                {"$set": update_dict}
            )
            
            if result.modified_count:
                updated_appointment = await self.collection.find_one({"_id": str(appointment_id)})
                updated_appointment["id"] = updated_appointment["_id"]
                return AppointmentOut(**updated_appointment)
        
        raise HTTPException(status_code=500, detail="Failed to update appointment")

    async def delete_appointment(self, appointment_id: UUID) -> bool:
        """Delete an appointment"""
        result = await self.collection.delete_one({"_id": str(appointment_id)})
        if result.deleted_count:
            return True
        raise HTTPException(status_code=404, detail="Appointment not found")

    async def _validate_appointment_references(self, appointment_data: AppointmentCreate):
        """Validate that all referenced entities exist"""
        # Check customer exists
        customer = await self.user_collection.find_one({"_id": str(appointment_data.customer_id)})
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")
        
        # Check clinic exists
        clinic = await self.clinic_collection.find_one({"_id": str(appointment_data.clinic_id)})
        if not clinic:
            raise HTTPException(status_code=404, detail="Clinic not found")
        
        # Check service exists
        service = await self.service_collection.find_one({"_id": str(appointment_data.service_id)})
        if not service:
            raise HTTPException(status_code=404, detail="Service not found")
        
        # Check staff exists
        staff = await self.staff_collection.find_one({"_id": str(appointment_data.staff_id)})
        if not staff:
            raise HTTPException(status_code=404, detail="Staff not found")
        
        # Validate that staff can provide the service
        if str(appointment_data.service_id) not in [str(sid) for sid in staff["service_ids"]]:
            raise HTTPException(status_code=400, detail="Staff member cannot provide this service")
        
        # Validate that staff belongs to the clinic
        if str(appointment_data.clinic_id) != str(staff["clinic_id"]):
            raise HTTPException(status_code=400, detail="Staff member does not belong to this clinic")

    async def _check_scheduling_conflicts(self, appointment_data: AppointmentCreate, exclude_appointment_id: Optional[UUID] = None):
        """Check for scheduling conflicts with existing appointments"""
        query = {
            "staff_id": str(appointment_data.staff_id),
            "status": {"$ne": AppStatus.canceled},
            "$or": [
                {
                    "start_time": {"$lte": appointment_data.start_time},
                    "end_time": {"$gt": appointment_data.start_time}
                },
                {
                    "start_time": {"$lt": appointment_data.end_time},
                    "end_time": {"$gte": appointment_data.end_time}
                },
                {
                    "start_time": {"$gte": appointment_data.start_time},
                    "end_time": {"$lte": appointment_data.end_time}
                }
            ]
        }
        
        # Exclude current appointment if updating
        if exclude_appointment_id:
            query["_id"] = {"$ne": str(exclude_appointment_id)}
        
        conflict = await self.collection.find_one(query)
        if conflict:
            raise HTTPException(status_code=400, detail="Time slot conflicts with existing appointment")


# Create a global instance
appointment_service = AppointmentService()
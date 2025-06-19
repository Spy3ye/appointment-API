from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Optional
from uuid import UUID
from bson import ObjectId
from database.collections import get_appointment_collection, get_user_collection, get_clinic_collection, get_service_collection, get_staff_collection
from schemas.Appointment import AppointmentCreate, AppointmentUpdate, AppointmentOut, AppointmentDetailedOut
from models.Appointment import Appointment, AppStatus
from utils.auth import decode_access_token
from fastapi.security import HTTPBearer

router = APIRouter()
security = HTTPBearer()

# Dependency to get current user
async def get_current_user(token: str = Depends(security)):
    try:
        payload = decode_access_token(token.credentials)
        user_id = payload.get("user_id")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_id
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

@router.post("/", response_model=AppointmentOut, status_code=status.HTTP_201_CREATED)
async def create_appointment(
    appointment_data: AppointmentCreate,
    current_user: str = Depends(get_current_user)
):
    """Create a new appointment"""
    collection = get_appointment_collection()
    user_collection = get_user_collection()
    clinic_collection = get_clinic_collection()
    service_collection = get_service_collection()
    staff_collection = get_staff_collection()
    
    # Verify customer exists
    customer = await user_collection.find_one({"_id": ObjectId(str(appointment_data.customer_id))})
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    # Verify clinic exists
    clinic = await clinic_collection.find_one({"_id": ObjectId(str(appointment_data.clinic_id))})
    if not clinic:
        raise HTTPException(status_code=404, detail="Clinic not found")
    
    # Verify service exists
    service = await service_collection.find_one({"_id": ObjectId(str(appointment_data.service_id))})
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    
    # Verify staff exists and can provide the service
    staff = await staff_collection.find_one({"_id": ObjectId(str(appointment_data.staff_id))})
    if not staff:
        raise HTTPException(status_code=404, detail="Staff not found")
    
    if str(appointment_data.service_id) not in staff.get("service_ids", []):
        raise HTTPException(status_code=400, detail="Staff cannot provide this service")
    
    # Check for scheduling conflicts
    existing_appointment = await collection.find_one({
        "staff_id": str(appointment_data.staff_id),
        "start_time": {"$lt": appointment_data.end_time},
        "end_time": {"$gt": appointment_data.start_time},
        "status": {"$ne": AppStatus.canceled.value}
    })
    
    if existing_appointment:
        raise HTTPException(status_code=400, detail="Staff is not available at this time")
    
    # Create appointment
    appointment = Appointment(**appointment_data.dict())
    appointment_dict = appointment.dict()
    appointment_dict["_id"] = ObjectId()
    appointment_dict["id"] = str(appointment_dict["_id"])
    appointment_dict["customer_id"] = str(appointment_dict["customer_id"])
    appointment_dict["clinic_id"] = str(appointment_dict["clinic_id"])
    appointment_dict["service_id"] = str(appointment_dict["service_id"])
    appointment_dict["staff_id"] = str(appointment_dict["staff_id"])
    appointment_dict["status"] = AppStatus.booked.value
    
    result = await collection.insert_one(appointment_dict)
    
    # Return created appointment
    created_appointment = await collection.find_one({"_id": result.inserted_id})
    created_appointment["id"] = str(created_appointment["_id"])
    
    return AppointmentOut(**created_appointment)

@router.get("/{appointment_id}", response_model=AppointmentOut)
async def get_appointment(
    appointment_id: UUID,
    current_user: str = Depends(get_current_user)
):
    """Get appointment by ID"""
    collection = get_appointment_collection()
    
    appointment = await collection.find_one({"_id": ObjectId(str(appointment_id))})
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    appointment["id"] = str(appointment["_id"])
    return AppointmentOut(**appointment)

@router.get("/", response_model=List[AppointmentOut])
async def get_appointments(
    skip: int = 0,
    limit: int = 100,
    customer_id: Optional[UUID] = None,
    staff_id: Optional[UUID] = None,
    clinic_id: Optional[UUID] = None,
    status: Optional[AppStatus] = None,
    current_user: str = Depends(get_current_user)
):
    """Get appointments with filters"""
    collection = get_appointment_collection()
    
    filter_query = {}
    if customer_id:
        filter_query["customer_id"] = str(customer_id)
    if staff_id:
        filter_query["staff_id"] = str(staff_id)
    if clinic_id:
        filter_query["clinic_id"] = str(clinic_id)
    if status:
        filter_query["status"] = status.value
    
    cursor = collection.find(filter_query).skip(skip).limit(limit)
    appointments = []
    
    async for appointment in cursor:
        appointment["id"] = str(appointment["_id"])
        appointments.append(AppointmentOut(**appointment))
    
    return appointments

@router.get("/customer/{customer_id}", response_model=List[AppointmentOut])
async def get_customer_appointments(
    customer_id: UUID,
    current_user: str = Depends(get_current_user)
):
    """Get all appointments for a customer"""
    collection = get_appointment_collection()
    
    cursor = collection.find({"customer_id": str(customer_id)})
    appointments = []
    
    async for appointment in cursor:
        appointment["id"] = str(appointment["_id"])
        appointments.append(AppointmentOut(**appointment))
    
    return appointments

@router.get("/staff/{staff_id}", response_model=List[AppointmentOut])
async def get_staff_appointments(
    staff_id: UUID,
    current_user: str = Depends(get_current_user)
):
    """Get all appointments for a staff member"""
    collection = get_appointment_collection()
    
    cursor = collection.find({"staff_id": str(staff_id)})
    appointments = []
    
    async for appointment in cursor:
        appointment["id"] = str(appointment["_id"])
        appointments.append(AppointmentOut(**appointment))
    
    return appointments

@router.put("/{appointment_id}", response_model=AppointmentOut)
async def update_appointment(
    appointment_id: UUID,
    appointment_update: AppointmentUpdate,
    current_user: str = Depends(get_current_user)
):
    """Update appointment"""
    collection = get_appointment_collection()
    
    # Check if appointment exists
    existing_appointment = await collection.find_one({"_id": ObjectId(str(appointment_id))})
    if not existing_appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    update_data = appointment_update.dict(exclude_unset=True)
    
    # If updating time, check for conflicts
    if "start_time" in update_data or "end_time" in update_data:
        staff_id = existing_appointment["staff_id"]
        start_time = update_data.get("start_time", existing_appointment["start_time"])
        end_time = update_data.get("end_time", existing_appointment["end_time"])
        
        conflict = await collection.find_one({
            "_id": {"$ne": ObjectId(str(appointment_id))},
            "staff_id": staff_id,
            "start_time": {"$lt": end_time},
            "end_time": {"$gt": start_time},
            "status": {"$ne": AppStatus.canceled.value}
        })
        
        if conflict:
            raise HTTPException(status_code=400, detail="Staff is not available at this time")
    
    # Convert status enum to string if present
    if "status" in update_data:
        update_data["status"] = update_data["status"].value
    
    result = await collection.update_one(
        {"_id": ObjectId(str(appointment_id))},
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    # Return updated appointment
    updated_appointment = await collection.find_one({"_id": ObjectId(str(appointment_id))})
    updated_appointment["id"] = str(updated_appointment["_id"])
    
    return AppointmentOut(**updated_appointment)

@router.delete("/{appointment_id}")
async def delete_appointment(
    appointment_id: UUID,
    current_user: str = Depends(get_current_user)
):
    """Delete appointment"""
    collection = get_appointment_collection()
    
    result = await collection.delete_one({"_id": ObjectId(str(appointment_id))})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    return {"message": "Appointment deleted successfully"}

@router.put("/{appointment_id}/cancel")
async def cancel_appointment(
    appointment_id: UUID,
    current_user: str = Depends(get_current_user)
):
    """Cancel appointment"""
    collection = get_appointment_collection()
    
    result = await collection.update_one(
        {"_id": ObjectId(str(appointment_id))},
        {"$set": {"status": AppStatus.canceled.value}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    return {"message": "Appointment canceled successfully"}

@router.put("/{appointment_id}/complete")
async def complete_appointment(
    appointment_id: UUID,
    current_user: str = Depends(get_current_user)
):
    """Mark appointment as completed"""
    collection = get_appointment_collection()
    
    result = await collection.update_one(
        {"_id": ObjectId(str(appointment_id))},
        {"$set": {"status": AppStatus.completed.value}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    return {"message": "Appointment completed successfully"}

# Export router
Appointment_router = router
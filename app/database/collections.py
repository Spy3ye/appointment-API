from database.database import get_database

def get_user_collection():
    return get_database()["users"]

def get_staff_collection():
    return get_database()["staff"]

def get_service_collection():
    return get_database()["services"]

def get_review_collection():
    return get_database()["reviews"]

def get_clinic_collection():
    return get_database()["clinics"]

def get_availability_collection():
    return get_database()["availability"]

def get_appointment_collection():
    return get_database()["appointments"]

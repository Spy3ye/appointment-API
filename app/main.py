from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from database.database import init_mongo
from routers.User import user_router
from routers.auth import auth_router
from routers import Availability , Appointment , Service , Staff , Review , Clinic
from routers.Appointment import Appointment_router
# from app.database import database , DatabaseManager  # Import the global instance here

app = FastAPI(
    title="Clinic Appoitment",
    description="Backend API for a Clinic Appointment",
    version="1.0.0"
)

init_mongo(app)


# @app.on_event("startup")
# async def startup_event():
#     """Initialize database on application startup"""
#     return db
#     # success = db.initialize()
#     # if success == False:
#     #     raise HTTPException(status_code=500, detail="❌ Failed to initialize the database")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with allowed origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router, tags=["Authentication"], prefix="/api/auth")
app.include_router(user_router, tags=["Users"], prefix="/api/users")
app.include_router(Availability.router)
app.include_router(Clinic.router)
app.include_router(Review.router)
app.include_router(Service.router)
app.include_router(Staff.router)




# app.include_router(product.router, tags=["Clinics"], prefix="/api/products")
# app.include_router(order.router, tags=["Appointments"], prefix="/api/orders")
# app.include_router(cart.router, tags=["Staff"], prefix="/api/cart")



@app.get("/", tags=["Root"])
async def root():
    return {
        "message": "E-Commerce API is running!",
        "version": "1.0.0",
        "status": "healthy"
    }



# Custom OpenAPI schema
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Clinic Appoitment",
        version="1.0.0",
        description="API for a modern Clinic Appoitment",
        routes=app.routes,
    )
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
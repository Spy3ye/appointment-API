from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from fastapi import FastAPI
from typing import Optional
from app.config import MONGO_URI, DATABASE_NAME

class MongoDB:
    client: Optional[AsyncIOMotorClient] = None
    db: Optional[AsyncIOMotorDatabase] = None

mongodb = MongoDB()

def connect_to_mongo():
    mongodb.client = AsyncIOMotorClient(MONGO_URI)
    mongodb.db = mongodb.client[DATABASE_NAME]
    print("✅ Connected to MongoDB")

def close_mongo_connection():
    if mongodb.client:
        mongodb.client.close()
        print("❌ MongoDB connection closed.")

def get_database() -> AsyncIOMotorDatabase:
    if not mongodb.db:
        raise Exception("Database not initialized.")
    return mongodb.db

def init_mongo(app: FastAPI):
    @app.on_event("startup")
    async def startup_db_client():
        connect_to_mongo()

    @app.on_event("shutdown")
    async def shutdown_db_client():
        close_mongo_connection()

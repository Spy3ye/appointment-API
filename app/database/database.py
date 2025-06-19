

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from fastapi import FastAPI
from config import MONGO_URI, DATABASE_NAME


client: AsyncIOMotorClient = None
db: AsyncIOMotorDatabase = None


def connect_to_mongo():
    global client, db
    try:
        client = AsyncIOMotorClient(MONGO_URI)
        db = client[DATABASE_NAME]
        print("✅ Connected to MongoDB")
    except Exception as e:
        print(f"❌ MongoDB connection error: {e}")


def close_mongo_connection():
    global client
    if client:
        client.close()
        print("❌ MongoDB connection closed.")


def get_database() -> AsyncIOMotorDatabase:
    # from database.database import db
    if db is None:
        raise Exception("❌ Database not initialized.")
    return db


def init_mongo(app):
    @app.on_event("startup")
    async def startup_db_client():
        connect_to_mongo()

    @app.on_event("shutdown")
    async def shutdown_db_client():
        close_mongo_connection()

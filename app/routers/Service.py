from fastapi import APIRouter, Depends, HTTPException, status
from schemas.User import UserCreate, UserOut
from services.User import UserService
from models.User import User
import traceback
from database.database import get_database

service_router = APIRouter()
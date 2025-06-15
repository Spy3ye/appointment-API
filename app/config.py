from dotenv import load_dotenv
import os

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DATABASE_NAME = os.getenv("DATABASE_NAME")
SECRET_KEY = os.getenv("SECRET_KEY")
SECRET_REFRESH_KEY = os.getenv("SECRET_REFRESH_KEY")
ALGORITHM = os.getenv("ALGORITHM")

import os
from dotenv import load_dotenv


load_dotenv()

class Settings:
    STORAGE_TYPE: str = os.getenv("STORAGE_TYPE", "in_memory")
    MONGO_URI: str = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    MONGO_DB_NAME: str = os.getenv("MONGO_DB_NAME", "suboptima_db")

settings = Settings()
from pydantic import BaseModel
import os


class Settings(BaseModel):
    api_prefix: str = "/api/v1"
    sqlite_url: str = os.getenv("SQLITE_URL", "sqlite:///./crash_reporter.db")
    mongo_url: str = os.getenv("MONGO_URL", "mongodb://localhost:27017")
    mongo_db: str = os.getenv("MONGO_DB", "crash_reporter")
    jwt_secret: str = os.getenv("JWT_SECRET", "change-me")
    jwt_algorithm: str = "HS256"


settings = Settings()

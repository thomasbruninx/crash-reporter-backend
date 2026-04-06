from fastapi import FastAPI

from app.api.routes import router
from app.core.config import settings
from app.db.mongo import init_mongo
from app.db.sql import Base, engine


app = FastAPI(
    title="Crash Reporter API",
    description="API for receiving and managing crash reports.",
    version="0.1.0",
    openapi_version="3.0.3",
    openapi_url="/openapi.json",
)


@app.on_event("startup")
async def startup_event():
    Base.metadata.create_all(bind=engine)
    await init_mongo()


app.include_router(router, prefix=settings.api_prefix)

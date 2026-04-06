from beanie import init_beanie
from pymongo import AsyncMongoClient

from app.core.config import settings
from app.documents.report import ReportDocument


mongo_client: AsyncMongoClient | None = None


async def init_mongo() -> None:
    global mongo_client
    mongo_client = AsyncMongoClient(settings.mongo_url)
    await init_beanie(database=mongo_client[settings.mongo_db], document_models=[ReportDocument])

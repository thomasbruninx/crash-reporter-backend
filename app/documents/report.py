from datetime import datetime, timezone
from uuid import uuid4

from beanie import Document
from pydantic import BaseModel, Field


class ReportDocument(Document):
    uuid: str = Field(default_factory=lambda: str(uuid4()))
    project_uuid: str
    instance_uuid: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(tz=timezone.utc))
    severity: str
    metadata: dict[str, object] = Field(default_factory=dict)

    class Settings:
        name = "reports"


class ReportQueryResult(BaseModel):
    items: list[ReportDocument]
    total: int
    page: int
    resultsperpage: int

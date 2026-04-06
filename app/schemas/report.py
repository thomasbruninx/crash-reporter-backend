from datetime import datetime
from pydantic import BaseModel, Field


class ReportCreate(BaseModel):
    instance_uuid: str
    severity: str = Field(pattern=r"^(low|medium|high|critical)$")
    metadata: dict[str, object] = Field(default_factory=dict)


class ReportUpdate(BaseModel):
    metadata: dict[str, object] = Field(default_factory=dict)


class ReportOut(BaseModel):
    uuid: str
    project_uuid: str
    instance_uuid: str
    timestamp: datetime
    severity: str
    metadata: dict[str, object]


class ReportQueryResponse(BaseModel):
    items: list[ReportOut]
    total: int
    page: int
    resultsperpage: int

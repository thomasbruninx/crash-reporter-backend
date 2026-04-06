from pydantic import BaseModel, Field
import re


PROJECT_ID_PATTERN = r"^[a-z0-9_-]+$"


class ProjectCreate(BaseModel):
    project_id: str = Field(pattern=PROJECT_ID_PATTERN)
    name: str


class ProjectUpdate(BaseModel):
    project_id: str | None = Field(default=None, pattern=PROJECT_ID_PATTERN)
    name: str | None = None


class ProjectOut(BaseModel):
    uuid: str
    project_id: str
    name: str


class ProjectQueryResponse(BaseModel):
    items: list[ProjectOut]
    total: int
    page: int
    resultsperpage: int

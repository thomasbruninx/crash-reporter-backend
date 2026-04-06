from pydantic import BaseModel


class InstanceCreate(BaseModel):
    project_id: str
    notes: str | None = None


class InstanceUpdate(BaseModel):
    notes: str


class InstanceOut(BaseModel):
    uuid: str
    project_uuid: str
    notes: str


class InstanceCreateResponse(BaseModel):
    instance_uuid: str
    token: str


class InstanceQueryResponse(BaseModel):
    items: list[InstanceOut]
    total: int
    page: int
    resultsperpage: int

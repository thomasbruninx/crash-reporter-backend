from datetime import datetime, timezone
from typing import Annotated
from uuid import uuid4

from beanie.odm.operators.find.comparison import In
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import select, or_, func
from sqlalchemy.orm import Session

from app.core.security import (
    ALL_SCOPES,
    create_token,
    hash_password,
    require_scope,
    verify_password,
    get_current_claims,
)
from app.db.sql import get_db
from app.documents.report import ReportDocument
from app.models.instance import Instance
from app.models.project import Project
from app.models.user import User
from app.schemas.auth import LoginRequest, TokenResponse
from app.schemas.instance import (
    InstanceCreate,
    InstanceCreateResponse,
    InstanceOut,
    InstanceQueryResponse,
    InstanceUpdate,
)
from app.schemas.project import ProjectCreate, ProjectOut, ProjectQueryResponse, ProjectUpdate
from app.schemas.report import ReportCreate, ReportOut, ReportQueryResponse, ReportUpdate
from app.schemas.user import UserCreate, UserOut


router = APIRouter()


def paginate(items: list, page: int, resultsperpage: int):
    total = len(items)
    if resultsperpage == 0:
        return items, total
    start = page * resultsperpage
    end = start + resultsperpage
    return items[start:end], total


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, response: Response, db: Session = Depends(get_db)):
    user = db.execute(select(User).where(User.username == payload.username)).scalar_one_or_none()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    token = create_token(sub=user.uuid, scopes=ALL_SCOPES, expires_seconds=3600)
    response.set_cookie("access_token", token, httponly=True, secure=False, samesite="lax", max_age=3600)
    return TokenResponse(access_token=token, expires_in_seconds=3600)


@router.post("/user", response_model=UserOut)
def create_user(payload: UserCreate, db: Session = Depends(get_db), _: dict = Depends(require_scope("user.create"))):
    existing = db.execute(select(User).where(User.username == payload.username)).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=409, detail="Username exists")
    user = User(uuid=str(uuid4()), username=payload.username, password_hash=hash_password(payload.password))
    db.add(user)
    db.commit()
    return UserOut(uuid=user.uuid, username=user.username)


@router.post("/project", response_model=ProjectOut)
def create_project(payload: ProjectCreate, db: Session = Depends(get_db), _: dict = Depends(require_scope("project.create"))):
    existing = db.execute(select(Project).where(Project.project_id == payload.project_id)).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=409, detail="project_id exists")
    project = Project(uuid=str(uuid4()), project_id=payload.project_id, name=payload.name)
    db.add(project)
    db.commit()
    return ProjectOut(uuid=project.uuid, project_id=project.project_id, name=project.name)


@router.get("/project/query", response_model=ProjectQueryResponse)
def query_projects(
    db: Session = Depends(get_db),
    uuids: Annotated[list[str] | None, Query()] = None,
    project_ids: Annotated[list[str] | None, Query()] = None,
    name: str | None = None,
    page: int = 0,
    resultsperpage: int = 25,
    _: dict = Depends(require_scope("project.read")),
):
    stmt = select(Project)
    if uuids:
        stmt = stmt.where(Project.uuid.in_(uuids))
    if project_ids:
        stmt = stmt.where(Project.project_id.in_(project_ids))
    if name:
        stmt = stmt.where(Project.name.ilike(f"%{name}%"))
    rows = db.execute(stmt).scalars().all()
    paged, total = paginate(rows, page, resultsperpage)
    return ProjectQueryResponse(
        items=[ProjectOut(uuid=i.uuid, project_id=i.project_id, name=i.name) for i in paged],
        total=total,
        page=page,
        resultsperpage=resultsperpage,
    )


@router.get("/project/{uuid}", response_model=ProjectOut)
def get_project(uuid: str, db: Session = Depends(get_db), _: dict = Depends(require_scope("project.read"))):
    project = db.execute(select(Project).where(Project.uuid == uuid)).scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Not found")
    return ProjectOut(uuid=project.uuid, project_id=project.project_id, name=project.name)


@router.put("/project/{uuid}", response_model=ProjectOut)
@router.patch("/project/{uuid}", response_model=ProjectOut)
def update_project(uuid: str, payload: ProjectUpdate, db: Session = Depends(get_db), _: dict = Depends(require_scope("project.update"))):
    project = db.execute(select(Project).where(Project.uuid == uuid)).scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Not found")
    if payload.project_id is not None:
        project.project_id = payload.project_id
    if payload.name is not None:
        project.name = payload.name
    db.add(project)
    db.commit()
    return ProjectOut(uuid=project.uuid, project_id=project.project_id, name=project.name)


@router.delete("/project/{uuid}")
async def delete_project(uuid: str, db: Session = Depends(get_db), _: dict = Depends(require_scope("project.delete"))):
    project = db.execute(select(Project).where(Project.uuid == uuid)).scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Not found")
    instances = db.execute(select(Instance).where(Instance.project_uuid == uuid)).scalars().all()
    instance_uuids = [i.uuid for i in instances]
    if instance_uuids:
        await ReportDocument.find(In(ReportDocument.instance_uuid, instance_uuids)).delete()
    for inst in instances:
        db.delete(inst)
    db.delete(project)
    db.commit()
    return {"status": "deleted"}


@router.post("/instance", response_model=InstanceCreateResponse)
def create_instance(payload: InstanceCreate, db: Session = Depends(get_db)):
    project = db.execute(select(Project).where(Project.project_id == payload.project_id)).scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    inst = Instance(uuid=str(uuid4()), project_uuid=project.uuid, notes=payload.notes or "")
    db.add(inst)
    db.commit()
    token = create_token(sub=inst.uuid, scopes=["report.create"], expires_seconds=25 * 365 * 24 * 3600, instance_uuid=inst.uuid)
    return InstanceCreateResponse(instance_uuid=inst.uuid, token=token)


@router.get("/instance/query", response_model=InstanceQueryResponse)
def query_instances(
    db: Session = Depends(get_db),
    uuids: Annotated[list[str] | None, Query()] = None,
    project_uuids: Annotated[list[str] | None, Query()] = None,
    project_ids: Annotated[list[str] | None, Query()] = None,
    page: int = 0,
    resultsperpage: int = 25,
    _: dict = Depends(require_scope("instance.read")),
):
    stmt = select(Instance)
    if uuids:
        stmt = stmt.where(Instance.uuid.in_(uuids))
    if project_uuids:
        stmt = stmt.where(Instance.project_uuid.in_(project_uuids))

    if project_ids:
        p_stmt = select(Project)
        if project_ids:
            p_stmt = p_stmt.where(Project.project_id.in_(project_ids))
        p_rows = db.execute(p_stmt).scalars().all()
        p_uuids = [p.uuid for p in p_rows]
        if not p_uuids:
            return InstanceQueryResponse(items=[], total=0, page=page, resultsperpage=resultsperpage)
        stmt = stmt.where(Instance.project_uuid.in_(p_uuids))

    rows = db.execute(stmt).scalars().all()
    paged, total = paginate(rows, page, resultsperpage)
    return InstanceQueryResponse(
        items=[InstanceOut(uuid=i.uuid, project_uuid=i.project_uuid, notes=i.notes) for i in paged],
        total=total,
        page=page,
        resultsperpage=resultsperpage,
    )


@router.get("/instance/{uuid}", response_model=InstanceOut)
def get_instance(uuid: str, db: Session = Depends(get_db), _: dict = Depends(require_scope("instance.read"))):
    inst = db.execute(select(Instance).where(Instance.uuid == uuid)).scalar_one_or_none()
    if not inst:
        raise HTTPException(status_code=404, detail="Not found")
    return InstanceOut(uuid=inst.uuid, project_uuid=inst.project_uuid, notes=inst.notes)


@router.put("/instance/{uuid}", response_model=InstanceOut)
@router.patch("/instance/{uuid}", response_model=InstanceOut)
def update_instance(uuid: str, payload: InstanceUpdate, db: Session = Depends(get_db), _: dict = Depends(require_scope("instance.update"))):
    inst = db.execute(select(Instance).where(Instance.uuid == uuid)).scalar_one_or_none()
    if not inst:
        raise HTTPException(status_code=404, detail="Not found")
    inst.notes = payload.notes
    db.add(inst)
    db.commit()
    return InstanceOut(uuid=inst.uuid, project_uuid=inst.project_uuid, notes=inst.notes)


@router.delete("/instance/{uuid}")
async def delete_instance(uuid: str, db: Session = Depends(get_db), _: dict = Depends(require_scope("instance.delete"))):
    inst = db.execute(select(Instance).where(Instance.uuid == uuid)).scalar_one_or_none()
    if not inst:
        raise HTTPException(status_code=404, detail="Not found")
    await ReportDocument.find(ReportDocument.instance_uuid == uuid).delete()
    db.delete(inst)
    db.commit()
    return {"status": "deleted"}


@router.post("/report", response_model=ReportOut)
async def create_report(payload: ReportCreate, db: Session = Depends(get_db), claims: dict = Depends(require_scope("report.create"))):
    if not isinstance(payload.metadata, dict):
        raise HTTPException(status_code=422, detail="metadata must be an object")

    inst = db.execute(select(Instance).where(Instance.uuid == payload.instance_uuid)).scalar_one_or_none()
    if not inst:
        raise HTTPException(status_code=404, detail="Instance not found")

    token_instance_uuid = claims.get("instance_uuid")
    if token_instance_uuid and token_instance_uuid != payload.instance_uuid:
        raise HTTPException(status_code=403, detail="Token instance mismatch")

    report = ReportDocument(
        project_uuid=inst.project_uuid,
        instance_uuid=payload.instance_uuid,
        severity=payload.severity,
        metadata=payload.metadata,
        timestamp=datetime.now(tz=timezone.utc),
    )
    await report.insert()
    return ReportOut(
        uuid=report.uuid,
        project_uuid=report.project_uuid,
        instance_uuid=report.instance_uuid,
        timestamp=report.timestamp,
        severity=report.severity,
        metadata=report.metadata,
    )


@router.get("/report/query", response_model=ReportQueryResponse)
async def query_reports(
    db: Session = Depends(get_db),
    uuids: Annotated[list[str] | None, Query()] = None,
    instance_uuids: Annotated[list[str] | None, Query()] = None,
    project_ids: Annotated[list[str] | None, Query()] = None,
    project_uuids: Annotated[list[str] | None, Query()] = None,
    project_name: str | None = None,
    severity: Annotated[list[str] | None, Query()] = None,
    page: int = 0,
    resultsperpage: int = 25,
    _: dict = Depends(require_scope("report.read")),
):
    filters = []
    if uuids:
        filters.append(In(ReportDocument.uuid, uuids))
    if instance_uuids:
        filters.append(In(ReportDocument.instance_uuid, instance_uuids))
    if severity:
        filters.append(In(ReportDocument.severity, severity))

    p_uuids = set(project_uuids or [])
    if project_ids or project_name:
        p_stmt = select(Project)
        if project_ids:
            p_stmt = p_stmt.where(Project.project_id.in_(project_ids))
        if project_name:
            p_stmt = p_stmt.where(Project.name.ilike(f"%{project_name}%"))
        p_rows = db.execute(p_stmt).scalars().all()
        p_uuids.update([p.uuid for p in p_rows])
    if project_ids or project_uuids or project_name:
        if not p_uuids:
            return ReportQueryResponse(items=[], total=0, page=page, resultsperpage=resultsperpage)
        filters.append(In(ReportDocument.project_uuid, list(p_uuids)))

    cursor = ReportDocument.find(*filters) if filters else ReportDocument.find_all()
    total = await cursor.count()
    if resultsperpage != 0:
        cursor = cursor.skip(page * resultsperpage).limit(resultsperpage)
    items = await cursor.to_list()
    return ReportQueryResponse(
        items=[
            ReportOut(
                uuid=i.uuid,
                project_uuid=i.project_uuid,
                instance_uuid=i.instance_uuid,
                timestamp=i.timestamp,
                severity=i.severity,
                metadata=i.metadata,
            )
            for i in items
        ],
        total=total,
        page=page,
        resultsperpage=resultsperpage,
    )


@router.get("/report/{uuid}", response_model=ReportOut)
async def get_report(uuid: str, _: dict = Depends(require_scope("report.read"))):
    report = await ReportDocument.find_one(ReportDocument.uuid == uuid)
    if not report:
        raise HTTPException(status_code=404, detail="Not found")
    return ReportOut(
        uuid=report.uuid,
        project_uuid=report.project_uuid,
        instance_uuid=report.instance_uuid,
        timestamp=report.timestamp,
        severity=report.severity,
        metadata=report.metadata,
    )


@router.put("/report/{uuid}", response_model=ReportOut)
@router.patch("/report/{uuid}", response_model=ReportOut)
async def update_report(uuid: str, payload: ReportUpdate, _: dict = Depends(require_scope("report.update"))):
    report = await ReportDocument.find_one(ReportDocument.uuid == uuid)
    if not report:
        raise HTTPException(status_code=404, detail="Not found")
    report.metadata = payload.metadata
    await report.save()
    return ReportOut(
        uuid=report.uuid,
        project_uuid=report.project_uuid,
        instance_uuid=report.instance_uuid,
        timestamp=report.timestamp,
        severity=report.severity,
        metadata=report.metadata,
    )


@router.delete("/report/{uuid}")
async def delete_report(uuid: str, _: dict = Depends(require_scope("report.delete"))):
    report = await ReportDocument.find_one(ReportDocument.uuid == uuid)
    if not report:
        raise HTTPException(status_code=404, detail="Not found")
    await report.delete()
    return {"status": "deleted"}

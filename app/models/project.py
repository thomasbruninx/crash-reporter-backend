from sqlalchemy import Column, String

from app.db.sql import Base


class Project(Base):
    __tablename__ = "projects"

    uuid = Column(String, primary_key=True, index=True)
    project_id = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=False, index=True)

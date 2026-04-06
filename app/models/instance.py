from sqlalchemy import Column, String, ForeignKey

from app.db.sql import Base


class Instance(Base):
    __tablename__ = "instances"

    uuid = Column(String, primary_key=True, index=True)
    project_uuid = Column(String, ForeignKey("projects.uuid", ondelete="CASCADE"), nullable=False, index=True)
    notes = Column(String, nullable=False, default="")

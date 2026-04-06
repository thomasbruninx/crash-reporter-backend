from sqlalchemy import Column, String

from app.db.sql import Base


class User(Base):
    __tablename__ = "users"

    uuid = Column(String, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)

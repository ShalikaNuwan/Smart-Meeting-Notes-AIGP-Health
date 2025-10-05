import enum
from sqlalchemy import Column, Integer, String, JSON, DateTime, Enum as SQLAlchemyEnum
from sqlalchemy.sql import func
from .database import Base

class MeetingStatus(str, enum.Enum):
    UPLOADED = "uploaded"
    TRANSCRIBED = "transcribed"
    SUMMARIZED = "summarized"
    DONE = "done"
    FAILED = "failed"

class Meeting(Base):
    __tablename__ = "meetings"
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String)
    storage_path = Column(String, unique=True)
    status = Column(SQLAlchemyEnum(MeetingStatus), default=MeetingStatus.UPLOADED)
    transcript = Column(JSON, nullable=True)
    summary = Column(JSON, nullable=True)
    action_items = Column(JSON, nullable=True)
    failure_reason = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
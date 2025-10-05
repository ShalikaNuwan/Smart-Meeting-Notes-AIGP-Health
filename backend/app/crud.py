from sqlalchemy.orm import Session
from . import models, schemas
from typing import Optional, Dict, Any

def get_meeting(db: Session, meeting_id: int):
    return db.query(models.Meeting).filter(models.Meeting.id == meeting_id).first()

def create_meeting(db: Session, filename: str, storage_path: str) -> models.Meeting:
    db_meeting = models.Meeting(filename=filename, storage_path=storage_path)
    db.add(db_meeting)
    db.commit()
    db.refresh(db_meeting)
    return db_meeting

def update_meeting(db: Session, meeting_id: int, **kwargs: Dict[str, Any]):
    db.query(models.Meeting).filter(models.Meeting.id == meeting_id).update(kwargs)
    db.commit()
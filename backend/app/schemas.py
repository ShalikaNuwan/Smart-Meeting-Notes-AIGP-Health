from pydantic import BaseModel
from typing import List, Optional, Any
from .models import MeetingStatus

class TranscriptSegment(BaseModel):
    start: float
    end: float
    text: str

class ActionItem(BaseModel):
    owner: Optional[str] = None
    due_date: Optional[str] = None
    priority: Optional[str] = None
    text: str

class MeetingCreateResponse(BaseModel):
    id: int
    filename: str
    status: MeetingStatus

class MeetingDetailsResponse(MeetingCreateResponse):
    transcript: Optional[Any] = None
    summary: Optional[Any] = None
    action_items: Optional[List[ActionItem]] = None
    failure_reason: Optional[str] = None

    class Config:
        from_attributes = True
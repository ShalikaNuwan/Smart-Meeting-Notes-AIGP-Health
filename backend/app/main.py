import os
import shutil
import uuid
from typing import Annotated
from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from . import crud, models, schemas, pipeline
from .database import SessionLocal, engine

# Create the database tables
models.Base.metadata.create_all(bind=engine)
app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


UPLOAD_DIRECTORY = "./uploads"
ALLOWED_CONTENT_TYPES = ["audio/mpeg", "audio/x-m4a", "audio/wav"]
os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)

@app.post("/meetings", response_model=schemas.MeetingCreateResponse)
async def create_meeting(
    background_tasks: BackgroundTasks,
    file: Annotated[UploadFile, File()],
    db: Session = Depends(get_db)
):
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(status_code=400, detail="Invalid audio file type.")

    original_filename = file.filename
    file_extension = os.path.splitext(original_filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    
    file_path = os.path.join(UPLOAD_DIRECTORY, unique_filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    meeting = crud.create_meeting(db=db, filename=file.filename, storage_path=file_path)

    # Add the long-running job to FastAPI's background tasks
    background_tasks.add_task(pipeline.run_pipeline, meeting_id=meeting.id, db=db)

    return meeting

@app.get("/meetings/{id}",response_model=schemas.MeetingDetailsResponse)
def get_meeting_details(id: int, db: Session = Depends(get_db)):
    """
    GET /meetings/:id endpoint:
    Returns the current status and results of a processing job.
    """
    db_meeting = crud.get_meeting(db, meeting_id=id)
    if db_meeting is None:
        raise HTTPException(status_code=404, detail="Meeting not found")
    
    response_data = schemas.MeetingDetailsResponse(
        id=db_meeting.id,
        filename=db_meeting.filename,
        status=db_meeting.status,
        summary=db_meeting.summary,
        action_items=db_meeting.action_items,
        failure_reason=db_meeting.failure_reason,
        transcript=db_meeting.transcript.get("segments") if db_meeting.transcript else None        
    )

    return response_data

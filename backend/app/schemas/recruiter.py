from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from app.schemas.job_posting import JobPostingResponse

class RecruiterProfileResponse(BaseModel):
    """Response schema for recruiter profile"""
    user_id: UUID
    email: str
    name: Optional[str] = None
    surname: Optional[str] = None
    recent_job_postings: List[JobPostingResponse] 
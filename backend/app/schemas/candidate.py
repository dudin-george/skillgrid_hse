from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime

class CandidateProfileCreate(BaseModel):
    """Request schema for creating/updating candidate profile"""
    skill_preset_id: Optional[UUID] = None

class AssessmentResult(BaseModel):
    """Schema for assessment result in candidate profile"""
    assessment_id: UUID
    assessment_date: datetime
    skill_results: Dict[str, float]  # skill_name: confirmation_percentage
    total_score: Optional[int] = None
    completion_time_minutes: Optional[int] = None
    status: str

class CandidateProfileResponse(BaseModel):
    """Response schema for candidate profile"""
    user_id: UUID
    email: str
    name: Optional[str] = None
    surname: Optional[str] = None
    skill_preset_id: Optional[UUID] = None
    skill_preset_name: Optional[str] = None
    last_assessment: Optional[AssessmentResult] = None 
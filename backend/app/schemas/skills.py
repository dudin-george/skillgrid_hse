from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime

class SubSkillResponse(BaseModel):
    id: UUID
    name: str
    
    class Config:
        from_attributes = True

class SkillResponse(BaseModel):
    id: UUID
    name: str
    level: int
    requirements: Optional[str] = None
    subskills: List[SubSkillResponse]
    
    class Config:
        from_attributes = True

class DomainResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str] = None
    skills: List[SkillResponse]
    
    class Config:
        from_attributes = True

class DomainListResponse(BaseModel):
    domains: List[DomainResponse]

class SkillInPresetResponse(BaseModel):
    id: UUID
    name: str
    domain_name: str
    level: int
    importance: int
    
    class Config:
        from_attributes = True

class SkillPresetResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str] = None
    complexity_level: int
    skills: List[SkillInPresetResponse]
    
    class Config:
        from_attributes = True

class SkillPresetListResponse(BaseModel):
    skill_presets: List[SkillPresetResponse]

class SkillDetailResponse(BaseModel):
    id: UUID
    name: str
    level: int
    requirements: Optional[str] = None
    domain_id: UUID
    domain_name: str
    subskills: List[SubSkillResponse]
    
    class Config:
        from_attributes = True

class AssessmentSkillResult(BaseModel):
    skill_id: UUID
    skill_name: str
    domain_name: str
    confirmation_percentage: float
    subskills_total: int
    subskills_confirmed: int
    
    class Config:
        from_attributes = True

class AssessmentDetailResponse(BaseModel):
    id: UUID
    assessment_date: datetime
    status: str
    total_score: Optional[int] = None
    completion_time_minutes: Optional[int] = None
    candidate_id: UUID
    skill_results: List[AssessmentSkillResult]
    
    class Config:
        from_attributes = True

class SkillPresetStatsResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str] = None
    complexity_level: int
    total_candidates: int
    avg_assessment_score: Optional[float] = None
    skill_count: int
    
    class Config:
        from_attributes = True

class SkillPresetStatsListResponse(BaseModel):
    skill_preset_stats: List[SkillPresetStatsResponse] 
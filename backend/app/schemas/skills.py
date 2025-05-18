from pydantic import BaseModel
from typing import List, Optional, Dict
from uuid import UUID

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
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
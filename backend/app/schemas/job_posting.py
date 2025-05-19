from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID
from app.schemas.company import CompanyResponse

class JobPostingBase(BaseModel):
    name: str
    description: Optional[str] = None
    status: Optional[str] = "open"

class JobPostingCreate(JobPostingBase):
    company_id: Optional[UUID] = Field(default=UUID('2e22cea2-dc4c-4550-ad98-5b2d6b3356f3'))

class JobPostingUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    final_candidate_id: Optional[UUID] = None

class JobPostingResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str] = None
    initiator_id: Optional[UUID] = None
    status: Optional[str] = "open"
    final_candidate_id: Optional[UUID] = None
    company: Optional[CompanyResponse] = None
    
    class Config:
        from_attributes = True 
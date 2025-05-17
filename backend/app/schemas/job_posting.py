from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID
from app.schemas.company import CompanyResponse

class JobPostingBase(BaseModel):
    name: str
    description: Optional[str] = None
    initiator_id: Optional[UUID] = None
    status: Optional[str] = "open"

class JobPostingCreate(JobPostingBase):
    company_id: Optional[UUID] = Field(default=UUID('719cb41b-6781-4418-879c-8a4789e4250a'))

class JobPostingUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    initiator_id: Optional[UUID] = None
    final_candidate_id: Optional[UUID] = None

class JobPostingResponse(JobPostingBase):
    id: UUID
    final_candidate_id: Optional[UUID] = None
    company: Optional[CompanyResponse] = None
    
    class Config:
        from_attributes = True 
from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID

class CompanyBase(BaseModel):
    name: str
    description: Optional[str] = None
    logo_url: Optional[str] = None

class CompanyCreate(CompanyBase):
    pass

class CompanyUpdate(CompanyBase):
    name: Optional[str] = None

class CompanyResponse(CompanyBase):
    id: UUID
    
    class Config:
        from_attributes = True 
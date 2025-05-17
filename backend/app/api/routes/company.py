from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.db.database import get_db
from app.models.models import Company
from app.schemas.company import CompanyCreate, CompanyResponse, CompanyUpdate

router = APIRouter()

@router.post("/company", response_model=CompanyResponse, status_code=status.HTTP_201_CREATED)
def create_company(company: CompanyCreate, db: Session = Depends(get_db)):
    db_company = Company(
        name=company.name,
        description=company.description,
        logo_url=company.logo_url
    )
    db.add(db_company)
    db.commit()
    db.refresh(db_company)
    return db_company

@router.get("/company/{company_id}", response_model=CompanyResponse)
def get_company(company_id: UUID, db: Session = Depends(get_db)):
    db_company = db.query(Company).filter(Company.id == company_id).first()
    if db_company is None:
        raise HTTPException(status_code=404, detail="Company not found")
    return db_company

@router.get("/company", response_model=List[CompanyResponse])
def get_companies(db: Session = Depends(get_db)):
    db_companies = db.query(Company).all()
    return db_companies

@router.put("/company/{company_id}", response_model=CompanyResponse)
def update_company(company_id: UUID, company: CompanyUpdate, db: Session = Depends(get_db)):
    db_company = db.query(Company).filter(Company.id == company_id).first()
    if db_company is None:
        raise HTTPException(status_code=404, detail="Company not found")
    
    # Update company fields if provided
    if company.name is not None:
        db_company.name = company.name
    if company.description is not None:
        db_company.description = company.description
    if company.logo_url is not None:
        db_company.logo_url = company.logo_url
    
    db.commit()
    db.refresh(db_company)
    return db_company 
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.db.database import get_db
from app.models.models import JobPosting, Company, CompanyJobPosting
from app.schemas.job_posting import JobPostingCreate, JobPostingResponse, JobPostingUpdate

router = APIRouter()

@router.post("/job", response_model=JobPostingResponse, status_code=status.HTTP_201_CREATED)
def create_job_posting(job_posting: JobPostingCreate, db: Session = Depends(get_db)):
    # Check if company exists
    company = db.query(Company).filter(Company.id == job_posting.company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    # Create job posting
    db_job_posting = JobPosting(
        name=job_posting.name,
        description=job_posting.description,
        initiator_id=job_posting.initiator_id,
        status=job_posting.status
    )
    db.add(db_job_posting)
    db.commit()
    db.refresh(db_job_posting)
    
    # Create company job posting relation
    db_company_job_posting = CompanyJobPosting(
        company_id=job_posting.company_id,
        job_posting_id=db_job_posting.id
    )
    db.add(db_company_job_posting)
    db.commit()
    
    # Add company to response
    setattr(db_job_posting, 'company', company)
    
    return db_job_posting

@router.get("/job", response_model=List[JobPostingResponse])
def get_job_postings(db: Session = Depends(get_db)):
    # Get all job postings with their related companies
    job_postings = db.query(JobPosting).join(
        CompanyJobPosting, CompanyJobPosting.job_posting_id == JobPosting.id
    ).join(
        Company, Company.id == CompanyJobPosting.company_id
    ).all()
    
    # Add company to each job posting
    for job_posting in job_postings:
        company = db.query(Company).join(
            CompanyJobPosting, CompanyJobPosting.company_id == Company.id
        ).filter(
            CompanyJobPosting.job_posting_id == job_posting.id
        ).first()
        setattr(job_posting, 'company', company)
    
    return job_postings

@router.get("/job/{job_id}", response_model=JobPostingResponse)
def get_job_posting(job_id: UUID, db: Session = Depends(get_db)):
    # Get the job posting
    job_posting = db.query(JobPosting).filter(JobPosting.id == job_id).first()
    if not job_posting:
        raise HTTPException(status_code=404, detail="Job posting not found")
    
    # Get the company for this job posting
    company = db.query(Company).join(
        CompanyJobPosting, CompanyJobPosting.company_id == Company.id
    ).filter(
        CompanyJobPosting.job_posting_id == job_posting.id
    ).first()
    
    # Add company to response
    setattr(job_posting, 'company', company)
    
    return job_posting

@router.put("/job/{job_id}", response_model=JobPostingResponse)
def update_job_posting(job_id: UUID, job_posting: JobPostingUpdate, db: Session = Depends(get_db)):
    # Get the job posting
    db_job_posting = db.query(JobPosting).filter(JobPosting.id == job_id).first()
    if not db_job_posting:
        raise HTTPException(status_code=404, detail="Job posting not found")
    
    # Update job posting fields if provided
    if job_posting.name is not None:
        db_job_posting.name = job_posting.name
    if job_posting.description is not None:
        db_job_posting.description = job_posting.description
    if job_posting.status is not None:
        db_job_posting.status = job_posting.status
    if job_posting.initiator_id is not None:
        db_job_posting.initiator_id = job_posting.initiator_id
    if job_posting.final_candidate_id is not None:
        db_job_posting.final_candidate_id = job_posting.final_candidate_id
    
    db.commit()
    db.refresh(db_job_posting)
    
    # Get the company for this job posting
    company = db.query(Company).join(
        CompanyJobPosting, CompanyJobPosting.company_id == Company.id
    ).filter(
        CompanyJobPosting.job_posting_id == job_id
    ).first()
    
    # Add company to response
    setattr(db_job_posting, 'company', company)
    
    return db_job_posting

@router.delete("/job/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_job_posting(job_id: UUID, db: Session = Depends(get_db)):
    # Get the job posting
    db_job_posting = db.query(JobPosting).filter(JobPosting.id == job_id).first()
    if not db_job_posting:
        raise HTTPException(status_code=404, detail="Job posting not found")
    
    # Delete related company_job_posting entries
    db.query(CompanyJobPosting).filter(CompanyJobPosting.job_posting_id == job_id).delete()
    
    # Delete the job posting
    db.delete(db_job_posting)
    db.commit()
    
    return None 
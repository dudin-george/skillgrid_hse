from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import Dict, Any, List
from uuid import UUID

from app.db.database import get_db
from app.models.models import JobPosting, Company, CompanyJobPosting
from app.schemas.recruiter import RecruiterProfileResponse
from app.schemas.job_posting import JobPostingResponse
from app.core.auth import require_recruiter, get_user_id, authenticated_user

router = APIRouter()

@router.get("/profile", response_model=RecruiterProfileResponse)
async def get_recruiter_profile(
    request: Request,
    db: Session = Depends(get_db),
    user_data: dict = Depends(require_recruiter),
    user_id: UUID = Depends(get_user_id)
):
    """
    Get the recruiter's profile information including recent job postings
    """
    # Extract basic information from auth
    identity = user_data.get("identity", {})
    traits = identity.get("traits", {})
    
    # Get the recruiter's 5 most recent job postings
    job_postings = db.query(JobPosting).filter(
        JobPosting.initiator_id == user_id
    ).order_by(JobPosting.created_at.desc()).limit(5).all()
    
    # Add company information to each job posting
    for job_posting in job_postings:
        company = db.query(Company).join(
            CompanyJobPosting, CompanyJobPosting.company_id == Company.id
        ).filter(
            CompanyJobPosting.job_posting_id == job_posting.id
        ).first()
        
        setattr(job_posting, 'company', company)
    
    # Return the profile with all information
    return RecruiterProfileResponse(
        user_id=user_id,
        email=traits.get("email"),
        name=traits.get("name"),
        surname=traits.get("surname"),
        recent_job_postings=job_postings
    ) 
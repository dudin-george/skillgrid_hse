from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.models.models import Domain, Skill, SubSkill
from app.schemas.skills import DomainResponse, DomainListResponse

router = APIRouter()

@router.get("", response_model=DomainListResponse)
def get_domains(db: Session = Depends(get_db)):
    """
    Get all domains with their skills and subskills
    """
    # Get all domains
    domains = db.query(Domain).filter(Domain.is_active == True).all()
    
    # Prepare results with nested structure
    result = []
    
    for domain in domains:
        # Get all skills for this domain
        skills = db.query(Skill).filter(
            Skill.domain_id == domain.id,
            Skill.is_active == True
        ).all()
        
        # Create skill list with subskills
        domain_skills = []
        for skill in skills:
            # Get all subskills for this skill
            subskills = db.query(SubSkill).filter(
                SubSkill.skill_id == skill.id,
                SubSkill.is_active == True
            ).all()
            
            # Add this skill with its subskills
            setattr(skill, 'subskills', subskills)
            domain_skills.append(skill)
        
        # Add skills to domain
        setattr(domain, 'skills', domain_skills)
        result.append(domain)
    
    return DomainListResponse(domains=result) 
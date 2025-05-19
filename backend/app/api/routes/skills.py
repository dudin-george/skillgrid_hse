from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from sqlalchemy import func

from app.db.database import get_db
from app.models.models import Domain, Skill, SubSkill, SkillPreset, SkillPresetSkill
from app.schemas.skills import DomainResponse, DomainListResponse, SkillPresetResponse, SkillPresetListResponse

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

@router.get("/skillpresets", response_model=SkillPresetListResponse)
def get_skill_presets(db: Session = Depends(get_db)):
    """
    Get all skill presets with their skills and metadata
    """
    # Get all skill presets
    presets = db.query(SkillPreset).filter(SkillPreset.is_active == True).all()
    
    # Prepare results with nested structure
    result = []
    
    for preset in presets:
        # Get all skills for this preset with their importance
        preset_skills_query = (
            db.query(
                Skill,
                Domain.name.label("domain_name"),
                SkillPresetSkill.importance
            )
            .join(Domain, Domain.id == Skill.domain_id)
            .join(SkillPresetSkill, SkillPresetSkill.skill_id == Skill.id)
            .filter(
                SkillPresetSkill.skill_preset_id == preset.id,
                Skill.is_active == True
            )
            .order_by(SkillPresetSkill.importance.desc())
        )
        
        preset_skills = []
        
        for skill, domain_name, importance in preset_skills_query:
            # Create a custom object with all needed fields
            skill_obj = {
                "id": skill.id,
                "name": skill.name,
                "domain_name": domain_name,
                "level": skill.level,
                "importance": importance
            }
            preset_skills.append(skill_obj)
        
        # Add skills to preset
        setattr(preset, 'skills', preset_skills)
        result.append(preset)
    
    return SkillPresetListResponse(skill_presets=result) 
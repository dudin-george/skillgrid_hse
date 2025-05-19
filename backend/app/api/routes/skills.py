from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from sqlalchemy import func, desc, select, and_
from uuid import UUID

from app.db.database import get_db
from app.models.models import (
    Domain, Skill, SubSkill, SkillPreset, SkillPresetSkill, 
    Assessment, AssessmentSubSkill
)
from app.schemas.skills import (
    DomainResponse, DomainListResponse, 
    SkillPresetResponse, SkillPresetListResponse,
    SkillDetailResponse, AssessmentDetailResponse,
    SkillPresetStatsResponse, SkillPresetStatsListResponse
)

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

@router.get("/skillpresets/{preset_id}", response_model=SkillPresetResponse)
def get_skill_preset_by_id(preset_id: UUID, db: Session = Depends(get_db)):
    """
    Get a specific skill preset by ID with its skills and metadata
    """
    # Get the skill preset
    preset = db.query(SkillPreset).filter(
        SkillPreset.id == preset_id,
        SkillPreset.is_active == True
    ).first()
    
    if not preset:
        raise HTTPException(status_code=404, detail="Skill preset not found")
    
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
    
    return preset

@router.get("/skill/{skill_id}", response_model=SkillDetailResponse)
def get_skill_by_id(skill_id: UUID, db: Session = Depends(get_db)):
    """
    Get detailed information about a specific skill by ID
    """
    # Get the skill with its domain
    skill_query = (
        db.query(
            Skill,
            Domain.name.label("domain_name"),
            Domain.id.label("domain_id")
        )
        .join(Domain, Domain.id == Skill.domain_id)
        .filter(
            Skill.id == skill_id,
            Skill.is_active == True
        )
    ).first()
    
    if not skill_query:
        raise HTTPException(status_code=404, detail="Skill not found")
    
    skill, domain_name, domain_id = skill_query
    
    # Get all subskills for this skill
    subskills = db.query(SubSkill).filter(
        SubSkill.skill_id == skill_id,
        SubSkill.is_active == True
    ).all()
    
    # Create a custom response object
    skill_detail = {
        "id": skill.id,
        "name": skill.name,
        "level": skill.level,
        "requirements": skill.requirements,
        "domain_id": domain_id,
        "domain_name": domain_name,
        "subskills": subskills
    }
    
    return skill_detail

@router.get("/assessment/{assessment_id}", response_model=AssessmentDetailResponse)
def get_assessment_by_id(assessment_id: UUID, db: Session = Depends(get_db)):
    """
    Get detailed assessment results by assessment ID
    """
    # Get the assessment
    assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
    
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    
    # Get all subskills in this assessment and their status
    assessment_subskills = db.query(AssessmentSubSkill).filter(
        AssessmentSubSkill.assessment_id == assessment_id
    ).all()
    
    # Group by skill to calculate confirmation percentage
    skill_results = []
    
    # First, gather all subskill IDs in this assessment
    subskill_ids = [as_subskill.subskill_id for as_subskill in assessment_subskills]
    
    # Get all subskills with their related skills and domains
    subskills_data = (
        db.query(
            SubSkill.id,
            SubSkill.skill_id,
            Skill.name.label("skill_name"),
            Domain.name.label("domain_name")
        )
        .join(Skill, Skill.id == SubSkill.skill_id)
        .join(Domain, Domain.id == Skill.domain_id)
        .filter(SubSkill.id.in_(subskill_ids))
    ).all()
    
    # Create a mapping of subskill ID to skill data
    subskill_to_skill = {
        subskill_id: (skill_id, skill_name, domain_name)
        for subskill_id, skill_id, skill_name, domain_name in subskills_data
    }
    
    # Count subskills by skill
    skill_subskill_counts = {}
    skill_confirmed_counts = {}
    
    for as_subskill in assessment_subskills:
        if as_subskill.subskill_id not in subskill_to_skill:
            continue
            
        skill_id, skill_name, domain_name = subskill_to_skill[as_subskill.subskill_id]
        
        if skill_id not in skill_subskill_counts:
            skill_subskill_counts[skill_id] = {
                "skill_id": skill_id,
                "skill_name": skill_name,
                "domain_name": domain_name,
                "total": 0,
                "confirmed": 0
            }
        
        skill_subskill_counts[skill_id]["total"] += 1
        if as_subskill.is_demonstrated:
            skill_subskill_counts[skill_id]["confirmed"] += 1
    
    # Calculate percentages and create results
    for skill_id, counts in skill_subskill_counts.items():
        percentage = counts["confirmed"] / counts["total"] if counts["total"] > 0 else 0
        
        skill_results.append({
            "skill_id": counts["skill_id"],
            "skill_name": counts["skill_name"],
            "domain_name": counts["domain_name"],
            "confirmation_percentage": percentage,
            "subskills_total": counts["total"],
            "subskills_confirmed": counts["confirmed"]
        })
    
    # Sort by confirmation percentage (highest first)
    skill_results.sort(key=lambda x: x["confirmation_percentage"], reverse=True)
    
    # Create a custom response object
    assessment_detail = {
        "id": assessment.id,
        "assessment_date": assessment.assessment_date,
        "status": assessment.status,
        "total_score": assessment.total_score,
        "completion_time_minutes": assessment.completion_time_minutes,
        "candidate_id": assessment.candidate_id,
        "skill_results": skill_results
    }
    
    return assessment_detail

@router.get("/skillpresets/stats", response_model=SkillPresetStatsListResponse)
def get_skill_preset_stats(db: Session = Depends(get_db)):
    """
    Get statistics for all skill presets including usage data
    """
    # Get all skill presets
    presets = db.query(SkillPreset).filter(SkillPreset.is_active == True).all()
    
    # Prepare results
    result = []
    
    for preset in presets:
        # Count skills in this preset
        skill_count = db.query(func.count(SkillPresetSkill.id)).filter(
            SkillPresetSkill.skill_preset_id == preset.id
        ).scalar() or 0
        
        # Count candidates using this preset (via metadata)
        # This would ideally use a proper relationship in the database
        # For now, we'll use a placeholder value
        total_candidates = 0  # Placeholder
        avg_assessment_score = None  # Placeholder
        
        # Create a stats object
        preset_stats = {
            "id": preset.id,
            "name": preset.name,
            "description": preset.description,
            "complexity_level": preset.complexity_level,
            "total_candidates": total_candidates,
            "avg_assessment_score": avg_assessment_score,
            "skill_count": skill_count
        }
        
        result.append(preset_stats)
    
    return SkillPresetStatsListResponse(skill_preset_stats=result)

@router.get("/popular", response_model=List[SkillDetailResponse])
def get_popular_skills(
    limit: Optional[int] = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """
    Get the most popular skills based on their usage in skill presets
    """
    # Count how many times each skill appears in presets
    popular_skills = (
        db.query(
            Skill,
            Domain.name.label("domain_name"),
            Domain.id.label("domain_id"),
            func.count(SkillPresetSkill.id).label("usage_count")
        )
        .join(Domain, Domain.id == Skill.domain_id)
        .join(SkillPresetSkill, SkillPresetSkill.skill_id == Skill.id)
        .filter(Skill.is_active == True)
        .group_by(Skill.id, Domain.id)
        .order_by(desc("usage_count"))
        .limit(limit)
        .all()
    )
    
    result = []
    
    for skill, domain_name, domain_id, _ in popular_skills:
        # Get subskills for this skill
        subskills = db.query(SubSkill).filter(
            SubSkill.skill_id == skill.id,
            SubSkill.is_active == True
        ).all()
        
        # Create skill detail object
        skill_detail = {
            "id": skill.id,
            "name": skill.name,
            "level": skill.level,
            "requirements": skill.requirements,
            "domain_id": domain_id,
            "domain_name": domain_name,
            "subskills": subskills
        }
        
        result.append(skill_detail)
    
    return result 
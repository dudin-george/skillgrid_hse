from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
from uuid import UUID

from app.db.database import get_db
from app.models.models import SkillPreset, Assessment, AssessmentSubSkill, Skill, SubSkill
from app.schemas.candidate import CandidateProfileCreate, CandidateProfileResponse, AssessmentResult
from app.core.auth import require_candidate, get_user_id, authenticated_user
from app.core.ory import ory_client

router = APIRouter()

@router.post("/profile", response_model=CandidateProfileResponse, status_code=status.HTTP_200_OK)
async def update_candidate_profile(
    profile_data: CandidateProfileCreate, 
    request: Request,
    db: Session = Depends(get_db),
    user_data: dict = Depends(require_candidate),
    user_id: UUID = Depends(get_user_id)
):
    """
    Update the candidate's profile by setting the skill preset
    
    This endpoint stores the skill preset in the user's Ory metadata_public field
    """
    metadata = {}
    
    # Validate skill preset if provided
    if profile_data.skill_preset_id:
        skill_preset = db.query(SkillPreset).filter(SkillPreset.id == profile_data.skill_preset_id).first()
        if not skill_preset:
            raise HTTPException(status_code=404, detail="Skill preset not found")
        
        # Add skill preset to metadata
        metadata["skill_preset_id"] = str(profile_data.skill_preset_id)
    
    # Update user metadata in Ory
    await ory_client.update_identity_metadata(str(user_id), metadata)
    
    # Get updated user info for response
    identity = user_data.get("identity", {})
    traits = identity.get("traits", {})
    
    # Get skill preset name if applicable
    skill_preset_name = None
    if profile_data.skill_preset_id:
        skill_preset = db.query(SkillPreset).filter(SkillPreset.id == profile_data.skill_preset_id).first()
        if skill_preset:
            skill_preset_name = skill_preset.name
    
    # Return the updated profile info
    return CandidateProfileResponse(
        user_id=user_id,
        email=traits.get("email"),
        name=traits.get("name"),
        surname=traits.get("surname"),
        skill_preset_id=profile_data.skill_preset_id,
        skill_preset_name=skill_preset_name,
        last_assessment=None  # No assessment data in this response
    )

@router.get("/profile", response_model=CandidateProfileResponse)
async def get_candidate_profile(
    request: Request,
    db: Session = Depends(get_db),
    user_data: dict = Depends(require_candidate),
    user_id: UUID = Depends(get_user_id)
):
    """
    Get the candidate's profile information including skill preset and assessment results
    """
    # Extract basic information from auth
    identity = user_data.get("identity", {})
    traits = identity.get("traits", {})
    metadata_public = identity.get("metadata_public", {}) or {}
    
    # Get skill preset information if available
    skill_preset_id = None
    skill_preset_name = None
    
    if metadata_public and "skill_preset_id" in metadata_public:
        try:
            skill_preset_id = UUID(metadata_public["skill_preset_id"])
            skill_preset = db.query(SkillPreset).filter(SkillPreset.id == skill_preset_id).first()
            if skill_preset:
                skill_preset_name = skill_preset.name
        except (ValueError, TypeError):
            # Invalid UUID in metadata, just ignore it
            pass
    
    # Get the most recent assessment for this user
    assessment = db.query(Assessment).filter(
        Assessment.candidate_id == user_id
    ).order_by(Assessment.assessment_date.desc()).first()
    
    last_assessment = None
    if assessment:
        # Calculate skill confirmation percentages
        skill_results = {}
        
        # Get all assessment_subskills for this assessment
        assessment_subskills = db.query(AssessmentSubSkill).filter(
            AssessmentSubSkill.assessment_id == assessment.id
        ).all()
        
        # Group by skill and calculate percentage
        skill_subskill_counts = {}
        skill_confirmed_counts = {}
        
        # Count total subskills and confirmed subskills for each skill
        for assessment_subskill in assessment_subskills:
            # Get the subskill
            subskill = db.query(SubSkill).filter(SubSkill.id == assessment_subskill.subskill_id).first()
            if not subskill:
                continue
                
            # Get the skill
            skill = db.query(Skill).filter(Skill.id == subskill.skill_id).first()
            if not skill:
                continue
                
            # Count this subskill
            skill_name = skill.name
            if skill_name not in skill_subskill_counts:
                skill_subskill_counts[skill_name] = 0
                skill_confirmed_counts[skill_name] = 0
                
            skill_subskill_counts[skill_name] += 1
            if assessment_subskill.is_demonstrated:
                skill_confirmed_counts[skill_name] += 1
        
        # Calculate percentages
        for skill_name in skill_subskill_counts:
            if skill_subskill_counts[skill_name] > 0:
                skill_results[skill_name] = skill_confirmed_counts[skill_name] / skill_subskill_counts[skill_name]
            else:
                skill_results[skill_name] = 0.0
        
        # Create assessment result object
        last_assessment = AssessmentResult(
            assessment_id=assessment.id,
            assessment_date=assessment.assessment_date,
            skill_results=skill_results,
            total_score=assessment.total_score,
            completion_time_minutes=assessment.completion_time_minutes,
            status=assessment.status
        )
    
    # Return the profile with all information
    return CandidateProfileResponse(
        user_id=user_id,
        email=traits.get("email"),
        name=traits.get("name"),
        surname=traits.get("surname"),
        skill_preset_id=skill_preset_id,
        skill_preset_name=skill_preset_name,
        last_assessment=last_assessment
    ) 
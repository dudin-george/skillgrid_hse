from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, select, and_
from typing import List, Optional, Dict, Any
from uuid import UUID
import json
from datetime import datetime, timedelta
import time

from app.db.database import get_db
from app.models.models import (
    Task, TaskSubSkill, Assessment, AssessmentSubSkill, 
    TaskSubmission, TaskTest, SkillPreset, SkillPresetSkill,
    Skill, SubSkill, Domain
)
from app.schemas.assessment import (
    StartAssessmentRequest, ActiveAssessmentResponse, TaskDetail, 
    CodeExample, CompileCodeRequest, CompileResult, SubmitTaskRequest,
    TaskSubmissionResult, AssessmentResultResponse, TaskDifficulty,
    AssessmentStatus, AssessmentTask, SkillResult, AssessmentListResponse
)
from app.core.auth import get_user_id, require_candidate, authenticated_user

router = APIRouter()

# Mock function to handle code compilation/execution
# In a real system, this would be a more sophisticated sandbox environment
def compile_and_execute_code(code: str, language: str, test_cases: List[Dict]) -> CompileResult:
    """
    Mock implementation to compile and execute code against test cases
    """
    try:
        # This is just a placeholder. In a real implementation, you would:
        # 1. Securely sandbox the code execution
        # 2. Run the code against test cases
        # 3. Return proper results

        # Let's simulate a simple compilation and test process
        if "error" in code.lower() or "exception" in code.lower():
            return CompileResult(
                success=False,
                errors="Compilation error: invalid syntax",
                execution_time_ms=None
            )
        
        # Simulate execution time
        execution_time = len(code) % 500  # Just a mock calculation
        
        # Basic simulation of test case execution
        output_samples = []
        for test_case in test_cases[:2]:  # Only show results for first two test cases
            output_samples.append(f"Input: {test_case.get('input', '')}\nExpected: {test_case.get('expected_output', '')}\nActual: <simulated output>")
        
        return CompileResult(
            success=True,
            output="\n\n".join(output_samples),
            execution_time_ms=execution_time
        )
    except Exception as e:
        return CompileResult(
            success=False,
            errors=f"Execution error: {str(e)}",
            execution_time_ms=None
        )

@router.post("/start", response_model=ActiveAssessmentResponse)
def start_assessment(
    request: Request,
    assessment_request: StartAssessmentRequest,
    db: Session = Depends(get_db),
    user_data: dict = Depends(require_candidate),
    user_id: UUID = Depends(get_user_id)
):
    """
    Start a new assessment for the authenticated candidate.
    This creates an assessment with selected tasks based on the skill preset.
    """
    # Get candidate ID from auth session - don't use the one from request if provided
    # This ensures we can only start assessments for ourselves
    candidate_id = user_id
    
    # Check if there's already an active assessment for this candidate
    existing_assessment = db.query(Assessment).filter(
        Assessment.candidate_id == candidate_id,
        Assessment.status == "in_progress"
    ).first()
    
    if existing_assessment:
        # Return the existing assessment instead of creating a new one
        return get_active_assessment(request, existing_assessment.id, db=db)
    
    # Determine which skill preset to use
    skill_preset = None
    if assessment_request.skill_preset_id:
        skill_preset = db.query(SkillPreset).filter(
            SkillPreset.id == assessment_request.skill_preset_id,
            SkillPreset.is_active == True
        ).first()
        
        if not skill_preset:
            raise HTTPException(status_code=404, detail="Skill preset not found")
    else:
        # Get a default skill preset (e.g., the first active one)
        skill_preset = db.query(SkillPreset).filter(
            SkillPreset.is_active == True
        ).first()
        
        if not skill_preset:
            raise HTTPException(status_code=404, detail="No active skill presets available")
    
    # Create a new assessment
    new_assessment = Assessment(
        candidate_id=candidate_id,
        assessment_date=datetime.utcnow(),
        status="in_progress"
    )
    db.add(new_assessment)
    db.flush()
    
    # Get skills from the selected preset
    preset_skills = db.query(SkillPresetSkill).filter(
        SkillPresetSkill.skill_preset_id == skill_preset.id
    ).all()
    
    skill_ids = [ps.skill_id for ps in preset_skills]
    
    # Get all subskills for these skills
    subskills = db.query(SubSkill).filter(
        SubSkill.skill_id.in_(skill_ids),
        SubSkill.is_active == True
    ).all()
    
    # Add subskills to the assessment
    for subskill in subskills:
        # Find matching preset skill to get importance
        preset_skill = next((ps for ps in preset_skills if ps.skill_id == subskill.skill_id), None)
        importance = preset_skill.importance if preset_skill else 1
        
        assessment_subskill = AssessmentSubSkill(
            assessment_id=new_assessment.id,
            subskill_id=subskill.id,
            importance=importance
        )
        db.add(assessment_subskill)
    
    # Find suitable tasks that test these subskills
    # For now, let's use a simple approach to get tasks that test the most relevant subskills
    task_query = (
        db.query(Task, func.count(TaskSubSkill.id).label("subskill_count"))
        .join(TaskSubSkill, TaskSubSkill.task_id == Task.id)
        .filter(
            TaskSubSkill.subskill_id.in_([s.id for s in subskills]),
            Task.is_active == True
        )
        .group_by(Task.id)
        .order_by(desc("subskill_count"))
        .limit(5)  # Limit to 5 tasks in the assessment
    ).all()
    
    tasks = [t[0] for t in task_query]
    
    if not tasks:
        # If no tasks match the subskills exactly, get some general tasks
        tasks = db.query(Task).filter(Task.is_active == True).limit(5).all()
    
    # Commit the transaction
    db.commit()
    
    # Return the active assessment details
    return get_active_assessment(request, new_assessment.id, db=db)

@router.get("/{assessment_id}", response_model=ActiveAssessmentResponse)
def get_active_assessment(
    request: Request,
    assessment_id: UUID,
    db: Session = Depends(get_db),
    user_data: dict = Depends(require_candidate),
    user_id: UUID = Depends(get_user_id)
):
    """
    Get the current state of an assessment, including current and remaining tasks
    """
    # Get the assessment
    assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    
    # Verify the assessment belongs to the authenticated user
    if assessment.candidate_id != user_id:
        raise HTTPException(status_code=403, detail="You don't have permission to access this assessment")
    
    # Get all subskills associated with this assessment
    assessment_subskills = db.query(AssessmentSubSkill).filter(
        AssessmentSubSkill.assessment_id == assessment_id
    ).all()
    
    subskill_ids = [as_subskill.subskill_id for as_subskill in assessment_subskills]
    
    # Find tasks that test these subskills
    task_query = (
        db.query(Task, func.count(TaskSubSkill.id).label("subskill_count"))
        .join(TaskSubSkill, TaskSubSkill.task_id == Task.id)
        .filter(
            TaskSubSkill.subskill_id.in_(subskill_ids),
            Task.is_active == True
        )
        .group_by(Task.id)
        .order_by(desc("subskill_count"))
        .limit(5)  # Limit to 5 tasks in the assessment
    ).all()
    
    potential_tasks = [t[0] for t in task_query]
    
    if not potential_tasks:
        # If no tasks match the subskills exactly, get some general tasks
        potential_tasks = db.query(Task).filter(Task.is_active == True).limit(5).all()
    
    # Get submissions for this assessment to determine completed tasks
    task_submissions = db.query(TaskSubmission).filter(
        TaskSubmission.assessment_id == assessment_id
    ).all()
    
    completed_task_ids = [sub.task_id for sub in task_submissions]
    
    # Separate tasks into completed and remaining
    completed_tasks = []
    remaining_tasks = []
    
    for task in potential_tasks:
        if task.id in completed_task_ids:
            # Find the submission to get score
            submission = next(sub for sub in task_submissions if sub.task_id == task.id)
            completed_tasks.append(AssessmentTask(
                task_id=task.id,
                title=task.title,
                difficulty=TaskDifficulty(task.difficulty.value),
                time_limit_minutes=task.time_limit_minutes,
                completed=True,
                score=submission.score
            ))
        else:
            remaining_tasks.append(AssessmentTask(
                task_id=task.id,
                title=task.title,
                difficulty=TaskDifficulty(task.difficulty.value),
                time_limit_minutes=task.time_limit_minutes,
                completed=False
            ))
    
    # Determine current task if any remaining
    current_task = None
    if remaining_tasks:
        task = db.query(Task).filter(Task.id == remaining_tasks[0].task_id).first()
        if task:
            # Convert examples from JSON to list of CodeExample objects
            examples = []
            try:
                if isinstance(task.examples, str):
                    examples_data = json.loads(task.examples)
                else:
                    examples_data = task.examples
                
                for example in examples_data:
                    examples.append(CodeExample(
                        input=example.get("input", ""),
                        output=example.get("output", ""),
                        explanation=example.get("explanation")
                    ))
            except:
                examples = []
            
            current_task = TaskDetail(
                id=task.id,
                title=task.title,
                description=task.description,
                instructions=task.instructions,
                difficulty=TaskDifficulty(task.difficulty.value),
                time_limit_minutes=task.time_limit_minutes,
                solution_template=task.solution_template,
                examples=examples
            )
    
    # Calculate estimated remaining time
    estimated_remaining_minutes = sum(task.time_limit_minutes for task in remaining_tasks)
    
    # Update assessment status if all tasks completed
    if not remaining_tasks and assessment.status == "in_progress":
        assessment.status = "completed"
        assessment.updated_at = datetime.utcnow()
        
        # Calculate total assessment time
        if task_submissions:
            first_submission = min(task_submissions, key=lambda ts: ts.created_at)
            last_submission = max(task_submissions, key=lambda ts: ts.updated_at)
            time_diff = (last_submission.updated_at - assessment.assessment_date).total_seconds() / 60
            assessment.completion_time_minutes = round(time_diff)
        
        # Calculate total score
        if task_submissions:
            total_score = sum(ts.score or 0 for ts in task_submissions)
            assessment.total_score = total_score
            
        db.commit()
    
    return ActiveAssessmentResponse(
        assessment_id=assessment.id,
        start_time=assessment.assessment_date,
        status=AssessmentStatus(assessment.status),
        current_task=current_task,
        completed_tasks=completed_tasks,
        remaining_tasks=remaining_tasks[1:] if remaining_tasks else [],  # First remaining task is the current task
        estimated_remaining_time_minutes=estimated_remaining_minutes
    )

@router.post("/compile", response_model=CompileResult)
def compile_code(
    request: Request,
    compile_request: CompileCodeRequest,
    db: Session = Depends(get_db),
    user_data: dict = Depends(authenticated_user)
):
    """
    Compile and run code to see the output without submitting
    """
    # For a real implementation, you would use a secure code execution environment
    # This is just a mock implementation
    
    # Get some test cases to use for demonstration
    test_cases = [
        {"input": "example_input_1", "expected_output": "example_output_1"},
        {"input": "example_input_2", "expected_output": "example_output_2"}
    ]
    
    # Compile and execute the code
    result = compile_and_execute_code(compile_request.code, compile_request.language, test_cases)
    
    return result

@router.post("/{assessment_id}/submit", response_model=TaskSubmissionResult)
def submit_task(
    request: Request,
    assessment_id: UUID,
    task_request: SubmitTaskRequest,
    db: Session = Depends(get_db),
    user_data: dict = Depends(require_candidate),
    user_id: UUID = Depends(get_user_id)
):
    """
    Submit a solution for a task in the assessment
    """
    # Verify the assessment exists and is in progress
    assessment = db.query(Assessment).filter(
        Assessment.id == assessment_id,
        Assessment.status == "in_progress"
    ).first()
    
    if not assessment:
        raise HTTPException(
            status_code=404, 
            detail="Assessment not found or already completed"
        )
    
    # Verify the assessment belongs to the authenticated user
    if assessment.candidate_id != user_id:
        raise HTTPException(status_code=403, detail="You don't have permission to access this assessment")
    
    # Verify the task exists
    task = db.query(Task).filter(Task.id == task_request.task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Check if this task has already been submitted
    existing_submission = db.query(TaskSubmission).filter(
        TaskSubmission.assessment_id == assessment_id,
        TaskSubmission.task_id == task_request.task_id
    ).first()
    
    if existing_submission:
        raise HTTPException(
            status_code=400, 
            detail="Task already submitted for this assessment"
        )
    
    # Get test cases for this task
    test_cases = db.query(TaskTest).filter(TaskTest.task_id == task.id).all()
    
    if not test_cases:
        # Use mock test cases if none exist in the database
        test_case_data = [
            {"input": "example_input_1", "expected_output": "example_output_1"},
            {"input": "example_input_2", "expected_output": "example_output_2"}
        ]
    else:
        test_case_data = [
            {
                "input": test.input_data, 
                "expected_output": test.expected_output
            } 
            for test in test_cases
        ]
    
    # Compile and execute the code
    compile_result = compile_and_execute_code(
        task_request.submitted_code, 
        "python",  # Assuming Python for now
        test_case_data
    )
    
    # For this mock implementation, we'll simulate scoring
    # In a real system, you would test against all test cases and compute a score
    
    # Simulate test outcomes
    is_correct = compile_result.success and "error" not in task_request.submitted_code.lower()
    score = task.points if is_correct else max(0, int(task.points * 0.3))  # 0 or partial credit
    
    # Create the submission record
    submission = TaskSubmission(
        task_id=task_request.task_id,
        assessment_id=assessment_id,
        submitted_code=task_request.submitted_code,
        is_correct=is_correct,
        score=score,
        execution_time_ms=compile_result.execution_time_ms,
        feedback="All tests passed!" if is_correct else "Some tests failed. Check your solution."
    )
    
    db.add(submission)
    
    # Now update the assessment subskills based on this submission
    
    # Get subskills that this task tests
    task_subskills = db.query(TaskSubSkill).filter(
        TaskSubSkill.task_id == task_request.task_id
    ).all()
    
    # Get assessment subskills
    assessment_subskills = db.query(AssessmentSubSkill).filter(
        AssessmentSubSkill.assessment_id == assessment_id,
        AssessmentSubSkill.subskill_id.in_([ts.subskill_id for ts in task_subskills])
    ).all()
    
    # Update assessment subskills based on task result
    for as_subskill in assessment_subskills:
        # Find matching task subskill to get importance
        task_subskill = next((ts for ts in task_subskills if ts.subskill_id == as_subskill.subskill_id), None)
        
        if task_subskill:
            if task_subskill.is_required:
                # Required subskills must have correct solution
                as_subskill.is_demonstrated = is_correct
            else:
                # Optional subskills can be partially demonstrated
                as_subskill.is_demonstrated = is_correct or (score > 0)
    
    db.commit()
    
    # Return the submission result
    return TaskSubmissionResult(
        task_id=task_request.task_id,
        is_correct=is_correct,
        score=score,
        execution_time_ms=compile_result.execution_time_ms,
        feedback=submission.feedback,
        compile_result=compile_result
    )

@router.get("/{assessment_id}/result", response_model=AssessmentResultResponse)
def get_assessment_result(
    request: Request,
    assessment_id: UUID,
    db: Session = Depends(get_db),
    user_data: dict = Depends(authenticated_user),
    user_id: UUID = Depends(get_user_id)
):
    """
    Get the detailed result of a completed assessment
    """
    # Get the assessment
    assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
    
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    
    # Verify the user has permission to view this assessment
    # Candidates can only view their own assessments
    # In a more complete solution, recruiters would have additional permissions
    identity = user_data.get("identity", {})
    traits = identity.get("traits", {})
    person_type = traits.get("person_type")
    
    if person_type == "candidate" and assessment.candidate_id != user_id:
        raise HTTPException(status_code=403, detail="You don't have permission to view this assessment")
    
    # Get submissions for this assessment
    task_submissions = db.query(TaskSubmission).filter(
        TaskSubmission.assessment_id == assessment_id
    ).all()
    
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
        
        skill_results.append(SkillResult(
            skill_id=counts["skill_id"],
            skill_name=counts["skill_name"],
            domain_name=counts["domain_name"],
            confirmation_percentage=percentage,
            subskills_total=counts["total"],
            subskills_confirmed=counts["confirmed"]
        ))
    
    # Sort by confirmation percentage (highest first)
    skill_results.sort(key=lambda x: x.confirmation_percentage, reverse=True)
    
    # Auto-complete if all tasks are submitted but status hasn't been updated
    if assessment.status == "in_progress":
        potential_tasks = (
            db.query(Task)
            .join(TaskSubSkill, TaskSubSkill.task_id == Task.id)
            .filter(
                TaskSubSkill.subskill_id.in_(subskill_ids),
                Task.is_active == True
            )
            .distinct(Task.id)
        ).count()
        
        if len(task_submissions) >= min(5, potential_tasks):  # Assuming 5 tasks max per assessment
            assessment.status = "completed"
            assessment.updated_at = datetime.utcnow()
            
            # Calculate total score if not already done
            if assessment.total_score is None:
                assessment.total_score = sum(ts.score or 0 for ts in task_submissions)
                
            # Calculate completion time if not already done
            if assessment.completion_time_minutes is None and task_submissions:
                first_submission = min(task_submissions, key=lambda ts: ts.created_at)
                last_submission = max(task_submissions, key=lambda ts: ts.updated_at)
                time_diff = (last_submission.updated_at - assessment.assessment_date).total_seconds() / 60
                assessment.completion_time_minutes = round(time_diff)
                
            db.commit()
    
    # Create a custom response object
    return AssessmentResultResponse(
        assessment_id=assessment.id,
        candidate_id=assessment.candidate_id,
        assessment_date=assessment.assessment_date,
        status=AssessmentStatus(assessment.status),
        total_score=assessment.total_score,
        completion_time_minutes=assessment.completion_time_minutes,
        skill_results=skill_results,
        tasks_completed=len(task_submissions),
        tasks_total=min(5, len(skill_results) * 2),  # Estimate based on skills
        feedback=assessment.feedback
    )

@router.get("/my/assessments", response_model=AssessmentListResponse)
def get_my_assessments(
    request: Request,
    limit: Optional[int] = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    user_data: dict = Depends(require_candidate),
    user_id: UUID = Depends(get_user_id)
):
    """
    Get all assessments for the authenticated candidate
    """
    # Get assessments for the authenticated user, ordered by most recent first
    assessments = db.query(Assessment).filter(
        Assessment.candidate_id == user_id
    ).order_by(desc(Assessment.assessment_date)).limit(limit).all()
    
    assessment_results = []
    
    for assessment in assessments:
        # Get the detailed result for each assessment
        result = get_assessment_result(request, assessment.id, db=db, user_data=user_data, user_id=user_id)
        assessment_results.append(result)
    
    return AssessmentListResponse(assessments=assessment_results)

# This endpoint is only for admin/recruiting purposes
@router.get("/candidate/{candidate_id}", response_model=AssessmentListResponse)
def get_candidate_assessments(
    request: Request,
    candidate_id: UUID,
    limit: Optional[int] = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    user_data: dict = Depends(require_recruiter)  # Only recruiters can view other candidates' assessments
):
    """
    Get all assessments for a specific candidate (recruiter only)
    """
    # Get assessments for this candidate, ordered by most recent first
    assessments = db.query(Assessment).filter(
        Assessment.candidate_id == candidate_id
    ).order_by(desc(Assessment.assessment_date)).limit(limit).all()
    
    assessment_results = []
    
    for assessment in assessments:
        # For each assessment, get the detailed results
        result = get_assessment_result(request, assessment.id, db=db, user_data=user_data, user_id=user_data.get("identity", {}).get("id"))
        assessment_results.append(result)
    
    return AssessmentListResponse(assessments=assessment_results) 
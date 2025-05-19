from pydantic import BaseModel
from typing import Optional, List, Dict, Any, Union
from uuid import UUID
from datetime import datetime
from enum import Enum

class AssessmentStatus(str, Enum):
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    EXPIRED = "expired"

class TaskDifficulty(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"

# Request schemas
class StartAssessmentRequest(BaseModel):
    candidate_id: Optional[UUID] = None
    skill_preset_id: Optional[UUID] = None

class SubmitTaskRequest(BaseModel):
    task_id: UUID
    submitted_code: str
    completion_time_seconds: Optional[int] = None

class CompileCodeRequest(BaseModel):
    code: str
    language: str = "python"

# Response schemas
class CodeExample(BaseModel):
    input: str
    output: str
    explanation: Optional[str] = None

class TaskDetail(BaseModel):
    id: UUID
    title: str
    description: str
    instructions: str
    difficulty: TaskDifficulty
    time_limit_minutes: int
    solution_template: Optional[str] = None
    examples: List[CodeExample]

class CompileResult(BaseModel):
    success: bool
    output: Optional[str] = None
    errors: Optional[str] = None
    execution_time_ms: Optional[int] = None

class TaskSubmissionResult(BaseModel):
    task_id: UUID
    is_correct: Optional[bool] = None
    score: Optional[int] = None
    execution_time_ms: Optional[int] = None
    feedback: Optional[str] = None
    compile_result: CompileResult

class AssessmentTask(BaseModel):
    task_id: UUID
    title: str
    difficulty: TaskDifficulty
    time_limit_minutes: int
    completed: bool
    score: Optional[int] = None

class ActiveAssessmentResponse(BaseModel):
    assessment_id: UUID
    start_time: datetime
    status: AssessmentStatus
    current_task: Optional[TaskDetail] = None
    completed_tasks: List[AssessmentTask] = []
    remaining_tasks: List[AssessmentTask] = []
    estimated_remaining_time_minutes: Optional[int] = None

class SkillResult(BaseModel):
    skill_id: UUID
    skill_name: str
    domain_name: str
    confirmation_percentage: float
    subskills_total: int
    subskills_confirmed: int

class AssessmentResultResponse(BaseModel):
    assessment_id: UUID
    candidate_id: UUID
    assessment_date: datetime
    status: AssessmentStatus
    total_score: Optional[int] = None
    completion_time_minutes: Optional[int] = None
    skill_results: List[SkillResult] = []
    tasks_completed: int
    tasks_total: int
    feedback: Optional[str] = None

class AssessmentListResponse(BaseModel):
    assessments: List[AssessmentResultResponse] 
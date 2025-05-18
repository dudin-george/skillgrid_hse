from sqlalchemy import Column, String, Integer, ForeignKey, Text, Boolean, DateTime, func, JSON, Enum, Table, ARRAY
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
import uuid
from datetime import datetime
import enum

Base = declarative_base()

class DifficultyLevel(enum.Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"

class Company(Base):
    __tablename__ = "companies"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    description = Column(Text)
    logo_url = Column(String)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

class JobPosting(Base):
    __tablename__ = "job_postings"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    description = Column(Text)
    initiator_id = Column(UUID(as_uuid=True))
    final_candidate_id = Column(UUID(as_uuid=True), nullable=True)
    status = Column(String, nullable=False, default="active")
    min_salary = Column(Integer, nullable=True)  # Salary in RUB
    max_salary = Column(Integer, nullable=True)  # Salary in RUB
    is_active = Column(Boolean, default=True, nullable=False)
    application_deadline = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

class JobApplication(Base):
    __tablename__ = "job_applications"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_posting_id = Column(UUID(as_uuid=True), ForeignKey("job_postings.id"), nullable=False)
    candidate_id = Column(UUID(as_uuid=True), nullable=False)
    initiator_id = Column(UUID(as_uuid=True), nullable=True)
    status = Column(String, nullable=False, default="pending")
    cover_letter = Column(Text)
    feedback = Column(Text)
    rejection_reason = Column(Text)
    interview_date = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

class JobSkill(Base):
    __tablename__ = "job_skills"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_posting_id = Column(UUID(as_uuid=True), ForeignKey("job_postings.id"), nullable=False)
    skill_id = Column(UUID(as_uuid=True), ForeignKey("skills.id"), nullable=False)
    importance = Column(Integer, default=1, nullable=False)  # 1-5 scale
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

class CompanyJobPosting(Base):
    __tablename__ = "company_job_postings"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    job_posting_id = Column(UUID(as_uuid=True), ForeignKey("job_postings.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

class Domain(Base):
    __tablename__ = "domains"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    description = Column(Text)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

class Skill(Base):
    __tablename__ = "skills"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    domain_id = Column(UUID(as_uuid=True), ForeignKey("domains.id"), nullable=False)
    name = Column(String, nullable=False)
    level = Column(Integer, nullable=False)
    requirements = Column(Text)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

class SubSkill(Base):
    __tablename__ = "subskills"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    skill_id = Column(UUID(as_uuid=True), ForeignKey("skills.id"), nullable=False)
    name = Column(String, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

class SkillPreset(Base):
    __tablename__ = "skill_presets"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    complexity_level = Column(Integer, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

class SkillPresetSkill(Base):
    __tablename__ = "skill_preset_skills"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    skill_preset_id = Column(UUID(as_uuid=True), ForeignKey("skill_presets.id"), nullable=False)
    skill_id = Column(UUID(as_uuid=True), ForeignKey("skills.id"), nullable=False)
    importance = Column(Integer, default=1, nullable=False)  # 1-5 scale
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

# New models for skill assessment tasks

class Task(Base):
    __tablename__ = "tasks"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    instructions = Column(Text, nullable=False)
    difficulty = Column(Enum(DifficultyLevel), default=DifficultyLevel.MEDIUM, nullable=False)
    time_limit_minutes = Column(Integer, default=30, nullable=False)
    points = Column(Integer, default=10, nullable=False)
    examples = Column(JSON, nullable=False)  # JSON array of input-output examples
    solution_template = Column(Text, nullable=True)  # Starter code template if needed
    solution_criteria = Column(Text, nullable=True)  # Explanation of evaluation criteria
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
class TaskSubSkill(Base):
    __tablename__ = "task_subskills"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_id = Column(UUID(as_uuid=True), ForeignKey("tasks.id"), nullable=False)
    subskill_id = Column(UUID(as_uuid=True), ForeignKey("subskills.id"), nullable=False)
    is_required = Column(Boolean, default=False, nullable=False)  # True for required, False for optional
    importance = Column(Integer, default=1, nullable=False)  # 1-5 scale
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

# New Assessment Model
class Assessment(Base):
    __tablename__ = "assessments"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    candidate_id = Column(UUID(as_uuid=True), nullable=False)
    assessment_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    status = Column(String, nullable=False, default="in_progress")  # in_progress, completed, failed
    total_score = Column(Integer, nullable=True)  # Total score of all tasks
    completion_time_minutes = Column(Integer, nullable=True)  # Total time taken
    feedback = Column(Text, nullable=True)  # Overall assessment feedback
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

# Assessment -> SubSkill mapping (what subskills were included in the assessment)
class AssessmentSubSkill(Base):
    __tablename__ = "assessment_subskills"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    assessment_id = Column(UUID(as_uuid=True), ForeignKey("assessments.id"), nullable=False)
    subskill_id = Column(UUID(as_uuid=True), ForeignKey("subskills.id"), nullable=False)
    is_demonstrated = Column(Boolean, nullable=True)  # Null if not evaluated, True/False for outcome
    importance = Column(Integer, default=1, nullable=False)  # 1-5 scale
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

# Update TaskSubmission model to link to assessment instead of job application
class TaskSubmission(Base):
    __tablename__ = "task_submissions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_id = Column(UUID(as_uuid=True), ForeignKey("tasks.id"), nullable=False)
    assessment_id = Column(UUID(as_uuid=True), ForeignKey("assessments.id"), nullable=False)  # Link to assessment instead of job app
    submitted_code = Column(Text, nullable=False)
    is_correct = Column(Boolean, nullable=True)  # Null if not yet evaluated
    score = Column(Integer, nullable=True)  # Null if not yet scored
    execution_time_ms = Column(Integer, nullable=True)  # Time taken to execute
    feedback = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

class TaskTest(Base):
    __tablename__ = "task_tests"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_id = Column(UUID(as_uuid=True), ForeignKey("tasks.id"), nullable=False)
    input_data = Column(Text, nullable=False)
    expected_output = Column(Text, nullable=False)
    is_hidden = Column(Boolean, default=False, nullable=False)  # Hidden tests not shown to candidates
    explanation = Column(Text, nullable=True)  # Explanation of what this test case verifies
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False) 
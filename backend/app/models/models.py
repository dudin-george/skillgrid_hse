from sqlalchemy import Column, String, Integer, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
import uuid

Base = declarative_base()

class Company(Base):
    __tablename__ = "companies"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    description = Column(Text)
    logo_url = Column(String)

class JobPosting(Base):
    __tablename__ = "job_postings"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    description = Column(Text)
    initiator_id = Column(UUID(as_uuid=True))
    final_candidate_id = Column(UUID(as_uuid=True), nullable=True)
    status = Column(String)

class JobSkill(Base):
    __tablename__ = "job_skills"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_posting_id = Column(UUID(as_uuid=True), ForeignKey("job_postings.id"), nullable=False)
    skill_id = Column(UUID(as_uuid=True), ForeignKey("skills.id"), nullable=False)

class CompanyJobPosting(Base):
    __tablename__ = "company_job_postings"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    job_posting_id = Column(UUID(as_uuid=True), ForeignKey("job_postings.id"), nullable=False)

class Domain(Base):
    __tablename__ = "domains"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    description = Column(Text)

class Skill(Base):
    __tablename__ = "skills"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    domain_id = Column(UUID(as_uuid=True), ForeignKey("domains.id"), nullable=False)
    name = Column(String, nullable=False)
    level = Column(Integer, nullable=False)
    requirements = Column(Text)

class SkillPreset(Base):
    __tablename__ = "skill_presets"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=True)
    name = Column(String, nullable=False)
    description = Column(Text)

class SkillPresetSkill(Base):
    __tablename__ = "skill_preset_skills"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    skill_preset_id = Column(UUID(as_uuid=True), ForeignKey("skill_presets.id"), nullable=False)
    skill_id = Column(UUID(as_uuid=True), ForeignKey("skills.id"), nullable=False) 
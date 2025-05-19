from fastapi import APIRouter
from app.api.routes.health import router as health_router
from app.api.routes.company import router as company_router
from app.api.routes.job_posting import router as job_posting_router
from app.api.routes.auth import router as auth_router
from app.api.routes.candidate import router as candidate_router
from app.api.routes.recruiter import router as recruiter_router
from app.api.routes.skills import router as skills_router

router = APIRouter()

router.include_router(health_router, tags=["health"])
router.include_router(company_router, tags=["companies"])
router.include_router(job_posting_router, tags=["job_postings"])
router.include_router(auth_router, prefix="/auth", tags=["auth"])
router.include_router(candidate_router, prefix="/candidate", tags=["candidate"])
router.include_router(recruiter_router, prefix="/recruiter", tags=["recruiter"])
router.include_router(skills_router, prefix="/domain", tags=["skills"]) 
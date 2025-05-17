from fastapi import APIRouter
from app.api.routes.health import router as health_router
from app.api.routes.company import router as company_router

router = APIRouter()

router.include_router(health_router, tags=["health"])
router.include_router(company_router, tags=["companies"]) 
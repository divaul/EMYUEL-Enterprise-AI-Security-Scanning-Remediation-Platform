"""
API Routes - Version 1

Main router that combines all API endpoints
"""

from fastapi import APIRouter

from .auth import router as auth_router
from .scans import router as scans_router
from .projects import router as projects_router
from .vulnerabilities import router as vulns_router
from .reports import router as reports_router
from .integrations import router as integrations_router
from .users import router as users_router

api_router = APIRouter()

# Include sub-routers
api_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
api_router.include_router(scans_router, prefix="/scans", tags=["Scans"])
api_router.include_router(projects_router, prefix="/projects", tags=["Projects"])
api_router.include_router(vulns_router, prefix="/vulnerabilities", tags=["Vulnerabilities"])
api_router.include_router(reports_router, prefix="/reports", tags=["Reports"])
api_router.include_router(integrations_router, prefix="/integrations", tags=["Integrations"])
api_router.include_router(users_router, prefix="/users", tags=["Users"])

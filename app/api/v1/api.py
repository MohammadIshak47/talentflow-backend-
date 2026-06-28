from fastapi import APIRouter

from app.api.v1.endpoints import analytics, applications, auth, candidates, interviews, jobs, stages

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(jobs.router)
api_router.include_router(stages.router)
api_router.include_router(applications.router)
api_router.include_router(interviews.router)
api_router.include_router(analytics.router)
api_router.include_router(candidates.router)

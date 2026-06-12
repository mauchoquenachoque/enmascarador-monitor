from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth,
    benchmarks,
    dashboard,
    databases,
    masking,
    metrics,
    queries,
)

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(databases.router)
api_router.include_router(queries.router)
api_router.include_router(masking.router)
api_router.include_router(metrics.router)
api_router.include_router(benchmarks.router)
api_router.include_router(dashboard.router)

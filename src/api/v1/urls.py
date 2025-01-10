from fastapi import APIRouter

from api.v1.handlers.auth import router as auth_router
from api.v1.handlers.tickets import router as tickets_router

v1_urls_router = APIRouter(prefix="/api/v1")

v1_urls_router.include_router(auth_router)
v1_urls_router.include_router(tickets_router)

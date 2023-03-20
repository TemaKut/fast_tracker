from fastapi import APIRouter

from .staff_tables.router import staff_router


tables_router = APIRouter(prefix='/tables')
tables_router.include_router(staff_router)

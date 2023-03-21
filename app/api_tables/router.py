from fastapi import APIRouter

from .staff_tables.router import staff_router
from .bdr_tables.router import bdr_router


tables_router = APIRouter(prefix='/tables')

tables_router.include_router(staff_router)
tables_router.include_router(bdr_router)

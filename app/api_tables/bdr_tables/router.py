from datetime import datetime

from fastapi import APIRouter  # Depends

# from app.api_auth.bad_responses import AuthExceptions
# from ..permissions import is_company_authorized_permission
from .schemas import BdrCommon, Project
from .utils import BdrTable, BdrByProjectsTable


bdr_router = APIRouter(
    prefix='/bdr',
    tags=['Таблицы БДР'],
    # dependencies=[Depends(is_company_authorized_permission)],
    # responses={
    #     401: AuthExceptions.ANAUTHORIZED.value,
    # },
)


@bdr_router.get(
    '/common/plan',
    response_model=BdrCommon,
)
async def bdr_plan(year: int = None):
    """ Эндпоинт таблицы БДР (План) """
    if not year:
        year = datetime.now().year

    table = BdrTable(year)
    result = await table.get_data()

    return result


@bdr_router.get('/common/fact', response_model=BdrCommon)
async def bdr_fact(year: int = None):
    """ Эндпоинт таблицы БДР (Факт) """
    if not year:
        year = datetime.now().year

    table = BdrTable(year)
    result = await table.get_data(is_plan=False)

    return result


@bdr_router.get('/by-projects/plan', response_model=dict[str, Project])
async def bdr_by_projects_plan(year: int = None):
    """ Эндпоинт таблицы БДР по проектам (План). """
    if not year:
        year = datetime.now().year

    table = BdrByProjectsTable(year)
    result = await table.get_data()

    return result


@bdr_router.get('/by-projects/fact', response_model=dict[str, Project])
async def bdr_by_projects_fact(year: int = None):
    """ Эндпоинт таблицы БДР по проектам (Факт). """
    if not year:
        year = datetime.now().year

    table = BdrByProjectsTable(year)
    result = await table.get_data(is_plan=False)

    return result

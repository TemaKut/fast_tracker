from datetime import datetime

from fastapi import APIRouter  # Depends

# from app.api_auth.bad_responses import AuthExceptions
# from ..permissions import is_company_authorized_permission
from .schemas import DdsCommon, Project
from .utils import DdsTable, DdsByProjects


dds_router = APIRouter(
    prefix='/dds',
    tags=['Таблицы ДДС'],
    # dependencies=[Depends(is_company_authorized_permission)],
    # responses={
    #     401: AuthExceptions.ANAUTHORIZED.value,
    # },
)


@dds_router.get('/common/plan', response_model=DdsCommon)
async def dds_plan(year: int = None):
    """ Эндпоинт таблицы ДДС (План) """
    if not year:
        year = datetime.now().year

    table = DdsTable(year)
    result = await table.get_data()

    return result


@dds_router.get('/common/fact', response_model=DdsCommon)
async def dds_fact(year: int = None):
    """ Эндпоинт таблицы ДДС (Факт) """
    if not year:
        year = datetime.now().year

    table = DdsTable(year)
    result = await table.get_data(is_plan=False)

    return result


@dds_router.get('/by-projects/plan', response_model=dict[str, Project])
async def dds_by_projects_plan(year: int = None):
    """ Эндпоинт таблицы ДДС (План) """
    if not year:
        year = datetime.now().year

    table = DdsByProjects(year)
    result = await table.get_data()

    return result


@dds_router.get('/by-projects/fact', response_model=dict[str, Project])
async def dds_by_projects_fact(year: int = None):
    """ Эндпоинт таблицы ДДС (Факт) """
    if not year:
        year = datetime.now().year

    table = DdsByProjects(year)
    result = await table.get_data(is_plan=False)

    return result

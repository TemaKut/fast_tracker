from datetime import datetime
from time import perf_counter

from fastapi import APIRouter  # Depends

# from app.api_auth.bad_responses import AuthExceptions
# from ..permissions import is_company_authorized_permission
from .utils import CommonWorkingTimeTable, WorkingTimeByProjectsTable
from .schemas import WorkingTime, WorkingTimeByMonthAndProjects


staff_router = APIRouter(
    prefix='/staff',
    tags=['Таблицы учёта рабочего времени'],
    # dependencies=[Depends(is_company_authorized_permission)],
    # responses={
    #     401: AuthExceptions.ANAUTHORIZED.value,
    # },
)


@staff_router.get('/common/plan', response_model=list[WorkingTime])
async def common_plan_table(year: int = None):
    """ Эндпоинт таблицы общ. рабочего времени (План). """
    if not year:
        year = datetime.now().year

    table = CommonWorkingTimeTable(year=year)
    table_data = await table.get_data()

    return table_data


@staff_router.get('/common/fact', response_model=list[WorkingTime])
async def common_fact_table(year: int = None):
    """ Эндпоинт таблицы общ. рабочего времени (Факт). """
    if not year:
        year = datetime.now().year

    table = CommonWorkingTimeTable(year=year)
    table_data = await table.get_data(is_plan=False)

    return table_data


@staff_router.get(
    '/by-projects/plan',
    response_model=WorkingTimeByMonthAndProjects,
)
async def by_projects_plan(year: int = None):
    """ Эндпоинт таблицы планового рабочего времени по проектам """
    if not year:
        year = datetime.now().year

    table = WorkingTimeByProjectsTable(year=year)
    table_data = await table.get_data()

    return WorkingTimeByMonthAndProjects(**table_data)


@staff_router.get(
    '/by-projects/fact',
    response_model=WorkingTimeByMonthAndProjects,
)
async def by_projects_fact(year: int = None):
    """ Эндпоинт таблицы планового рабочего времени по проектам """
    if not year:
        year = datetime.now().year

    table = WorkingTimeByProjectsTable(year=year)
    table_data = await table.get_data(is_plan=False)

    return WorkingTimeByMonthAndProjects(**table_data)

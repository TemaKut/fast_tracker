from datetime import datetime

from fastapi import APIRouter

from .utils import (
    CommonWorkingTimePlanTable, CommonWorkingTimeFactTable,
    WorkingTimeByProjectsTable, WorkingTimeByProjectsFactTable,
)
from .schemas import WorkingTime, WorkingTimeByMonthAndProjects


staff_router = APIRouter(
    prefix='/staff',
    tags=['Таблицы учёта рабочего времени']
)


@staff_router.get('/common/plan', response_model=list[WorkingTime])
async def common_plan_table(year: int = datetime.now().year):
    """ Эндпоинт таблицы общ. рабочего времени (План). """
    table = CommonWorkingTimePlanTable(year=year)
    table_data = await table.get_data()

    return table_data


@staff_router.get('/common/fact', response_model=list[WorkingTime])
async def common_fact_table(year: int = datetime.now().year):
    """ Эндпоинт таблицы общ. рабочего времени (Факт). """
    table = CommonWorkingTimeFactTable(year=year)
    table_data = await table.get_data()

    return table_data


@staff_router.get(
    '/by-projects/plan',
    response_model=WorkingTimeByMonthAndProjects,
)
async def by_projects_plan(year: int = datetime.now().year):
    """ Эндпоинт таблицы планового рабочего времени по проектам """
    table = WorkingTimeByProjectsTable(year=year)
    table_data = await table.get_data()

    return table_data


@staff_router.get(
    '/by-projects/fact',
    response_model=WorkingTimeByMonthAndProjects,
)
async def by_projects_fact(year: int = datetime.now().year):
    """ Эндпоинт таблицы планового рабочего времени по проектам """
    table = WorkingTimeByProjectsFactTable(year=year)
    table_data = await table.get_data()

    return table_data

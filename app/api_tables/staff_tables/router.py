from datetime import datetime

from fastapi import APIRouter

from .utils.staff_tables_utils import (
    CommonWorkingTimeTable, WorkingTimeByProjectsTable,
)
from .schemas import WorkingTime


staff_router = APIRouter(
    prefix='/staff',
    tags=['Таблицы учёта рабочего времени']
)


@staff_router.get('/common/plan', response_model=list[WorkingTime])
async def common_plan_table(year: int = datetime.now().year):
    """ Эндпоинт таблицы планового рабочего времени. """
    tables = CommonWorkingTimeTable(year=year)
    table_data = await tables.get_data()

    return table_data


@staff_router.get('/by-projects/plan')
async def by_projects_plan(year: int = datetime.now().year):
    """ Эндпоинт таблицы планового рабочего времени по проектам """
    tables = WorkingTimeByProjectsTable(year=year)
    table_data = await tables.get_data()

    return {}

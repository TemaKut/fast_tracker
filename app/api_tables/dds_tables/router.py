from datetime import datetime

from fastapi import APIRouter

from .schemas import DdsCommon
from .utils import DdsPlanTable, DdsFactTable


dds_router = APIRouter(
    prefix='/dds',
    tags=['Таблицы ДДС']
)


@dds_router.get('/common/plan', response_model=DdsCommon)
async def dds_plan(year: int = datetime.now().year):
    """ Эндпоинт таблицы ДДС (План) """
    table = DdsPlanTable(year)
    result = await table.get_data()

    return result


@dds_router.get('/common/fact', response_model=DdsCommon)
async def dds_fact(year: int = datetime.now().year):
    """ Эндпоинт таблицы ДДС (Факт) """
    table = DdsFactTable(year)
    result = await table.get_data()

    return result

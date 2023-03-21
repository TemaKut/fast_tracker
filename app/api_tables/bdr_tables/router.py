from datetime import datetime

from fastapi import APIRouter

from .schemas import Bdr
from .utils import BdrPlanTable


bdr_router = APIRouter(
    prefix='/bdr',
    tags=['Таблицы БДР']
)


@bdr_router.get('/plan', response_model=Bdr)
async def bdr_plan(year: int = datetime.now().year):
    """ Эндпоинт таблицы БДР (План) """
    table = BdrPlanTable(year)
    result = await table.get_data()

    return result

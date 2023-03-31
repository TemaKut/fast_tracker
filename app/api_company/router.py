from fastapi import APIRouter, Depends

from .jwt import get_current_company
from app.api_auth.bad_responses import AuthExceptions


company_router = APIRouter(prefix='/company', tags=['Company'])


@company_router.get(
    '/my_company',
    responses={
        401: AuthExceptions.ANAUTHORIZED.value,
    },
)
async def get_info_about_company(
    company=Depends(get_current_company),
):
    """ Получить информацию о текущей компании. """

    return company

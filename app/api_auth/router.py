from fastapi import APIRouter, Body, Depends

from .models import CompanyForTokenSchema, Company
from .jwt import get_access_token, get_current_company
from .bad_responses import AuthExceptions


auth_router = APIRouter(prefix='/auth', tags=['Authentication'])


@auth_router.post(
    '/token',
    responses={
        404: AuthExceptions.COMPANY_NOT_FOUND.value,
        400: AuthExceptions.COMPANY_INVALID_PASSWORD.value,
    },
)
async def get_token(body: CompanyForTokenSchema = Body()):
    """ Получить jwt токен. """
    company = await Company.get_or_none(login=body.login)

    token = await get_access_token(company, body)

    return token


@auth_router.get('/my_company')
async def get_info_about_company(
    company=Depends(get_current_company),
):
    """ Получить информацию о текущей компании. """

    return company

from fastapi import HTTPException, status, Request

from app.api_auth.jwt import decode_access_jwt_token_to_data
from .models import Company
from app.settings import log


async def get_current_company(request: Request) -> dict:
    """ Расшифровать токен из запроса. """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        token = request.headers.get('authorization')
        token = token.split(' ')[1]

        data = decode_access_jwt_token_to_data(token)

    except Exception as e:
        log.critical(f'Не удалось получить токен: {e}')
        raise credentials_exception

    db_company = await Company.get_or_none(login=data.get('login'))

    if not db_company:
        log.critical('Токен не связан с компанией.')
        raise credentials_exception

    return data

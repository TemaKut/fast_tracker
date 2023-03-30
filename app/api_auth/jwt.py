from datetime import timedelta, datetime

from fastapi import Body, HTTPException, status
from passlib.context import CryptContext
from jose import jwt

from app.api_company.models import Company, CompanyAllSchema
from app.settings import settings as sett


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    """ Верифицировать пароль с паролем в БД. """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    """ Получить хэш пароля (Обязательно при занесении в БД) """

    return pwd_context.hash(password)


def authenticate_company(company: Company, request_body: Body) -> Company:
    """ Подтверждение того что переданные данные компании валидны. """
    if not verify_password(request_body.password, company.password):

        return False

    return company


def encode_data_to_access_token(data: dict):
    """ Кодировать данные в jwt токен """
    # Кодировать в jwt
    encoded_jwt = jwt.encode(
        data, sett.SECRET_KEY, algorithm=sett.ALGORITHM,
    )

    return encoded_jwt


def decode_access_jwt_token_to_data(token: str) -> CompanyAllSchema:
    """ Декодировать токен в данные о компании. """
    payload = jwt.decode(token, sett.SECRET_KEY, algorithms=[sett.ALGORITHM])

    return payload.get('data')


async def get_access_token(company: Company, body: Body) -> dict:
    """ Получить jwt токен. """
    try:
        company = await CompanyAllSchema.from_tortoise_orm(company)

    except AttributeError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Company not found',
        )

    # Сравнение пароля в БД с представленным в теле запроса
    if not authenticate_company(company, body):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Invalid password',
        )

    token_expires = timedelta(minutes=sett.ACCESS_TOKEN_EXPIRE_MINUTES)
    # Действителен до..
    expire = datetime.utcnow() + token_expires
    token = encode_data_to_access_token(
        data={'data': company.dict(), 'exp': expire}
    )
    data = {
        'access_token': token,
        'token_type': sett.ACCESS_TOKEN_PREFIX,
    }

    return data

from enum import Enum


class AuthExceptions(Enum):
    """ Описание документации для ошибок  """

    ANAUTHORIZED = {"description": "Authorization required"}
    COMPANY_NOT_FOUND = {"description": "Company not found"}
    COMPANY_INVALID_PASSWORD = {"description": "Invalid password"}

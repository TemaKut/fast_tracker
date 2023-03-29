from enum import Enum


class AuthExceptions(Enum):
    """ Описание документации для ошибок  """

    COMPANY_NOT_FOUND = {
        "description": "Company not found",
        "content": {
            "application/json": {
                "schema": {
                    "$ref": "#/components/schemas/Message"
                }
            }
        }
    }
    COMPANY_INVALID_PASSWORD = {
        "description": "Invalid password",
        "content": {
            "application/json": {
                "schema": {
                    "$ref": "#/components/schemas/Message"
                }
            }
        }
    }

from fastapi import Depends

from app.api_auth.jwt import get_current_company


def is_company_authorized_permission(company=Depends(get_current_company)):
    """ Если компания авторизована - предоставить доступ к эндпоинту. """
    pass

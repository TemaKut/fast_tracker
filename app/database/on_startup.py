import os

from dotenv import load_dotenv

from app.api_company.models import Company


load_dotenv()


async def create_template_of_company():
    """ Создать шаблон компании при старте приложения. """
    password = os.getenv('COMPANY_PASSWORD')
    login = os.getenv('COMPANY_LOGIN')
    email = os.getenv('COMPANY_EMAIL')

    env_company = await Company.get_or_none(login=login, email=email)

    if not env_company:

        await Company.get_or_create(
            login=login,
            password=password,
            email=email,
        )

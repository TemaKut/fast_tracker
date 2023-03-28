import os

from dotenv import load_dotenv

from app.api_auth.models import Company


load_dotenv()


async def create_template_of_company():
    """ Создать шаблон компании при старте приложения. """
    await Company.get_or_create(
        login=os.getenv('COMPANY_LOGIN'),
        hashed_password=os.getenv('COMPANY_PASSWORD'),
        email=os.getenv('COMPANY_EMAIL'),
    )

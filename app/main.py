from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from tortoise.contrib.fastapi import register_tortoise

from .utils import tracker_api
from .api_tables.router import tables_router
from .settings import settings
from .database.on_startup import create_template_of_company


app = FastAPI()

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
)

# Регистрация базы данных
register_tortoise(
    app,
    db_url=settings.DATABASE_URL,
    modules={'models': ['app.api_auth.models']},
    generate_schemas=True,
)


@app.on_event('startup')
async def on_startup():
    """ Действия при старте приложения. """
    # Создать дефолтный шаблон компании используя .env
    await create_template_of_company()

    # Фоновая задача для получения списка задач из трекера
    await tracker_api.get_all_issues_from_tracker()


app.include_router(tables_router, prefix='/api/v1')

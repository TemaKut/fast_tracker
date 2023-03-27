from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from tortoise.contrib.fastapi import register_tortoise

from .utils import tracker_api
from .api_tables.router import tables_router
from .settings import settings


app = FastAPI()

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
)


@app.on_event('startup')
async def on_startup():
    """ Действия при старте приложения. """
    # Фоновая задача для получения списка задач из трекера
    tracker_api.get_all_issues_from_tracker()

app.include_router(tables_router, prefix='/api/v1')

# Регистрация базы данных
register_tortoise(
    app,
    db_url=settings.DATABASE_URL,
    modules={'models': ['app.api_users.models']},
    generate_schemas=True,
)

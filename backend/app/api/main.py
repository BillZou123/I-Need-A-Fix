from fastapi import APIRouter

from app.api.routes import appointments, doctors, items, login, private, users, utils
from app.core.config import settings

api_router = APIRouter() # this is for grouping endpoints together.
api_router.include_router(login.router) # each router file define its own router with a prefix, app/api/main.py collects them.
api_router.include_router(users.router)
api_router.include_router(utils.router)
api_router.include_router(items.router)
api_router.include_router(doctors.router)
api_router.include_router(appointments.router)


if settings.ENVIRONMENT == "local":
    api_router.include_router(private.router)

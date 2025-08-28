from contextlib import asynccontextmanager

from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from loguru import logger

from app.api.routers import all_routers
from app.config.redis import redis_for_auth
from app.exceptions.users import UserAlreadyExistsError


@asynccontextmanager
async def lifespan(client: FastAPI):
    try:
        await redis_for_auth.connect()
        yield
    except Exception as e:
        logger.exception(f"{e}")
    finally:
        await redis_for_auth.disconnect()


app = FastAPI(lifespan=lifespan)


for router in all_routers:
    app.include_router(router)


@app.get("/health", include_in_schema=False)
def health_check() -> dict:
    """Эндпойнт для проверки жизни приложения"""
    return {"status": "healthy"}


@app.exception_handler(UserAlreadyExistsError)
async def user_already_exists_exception_handler(request, exc: UserAlreadyExistsError):
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": "Пользователь уже существует"},
    )

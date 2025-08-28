from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import Response

from app.config.main import settings
from app.models.user import User
from app.schemas.user import SUserAuth, SUserRegister
from app.services.users import UserService
from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register/", status_code=status.HTTP_201_CREATED, summary="Регистрация пользователя")
async def register_user(user_data: SUserRegister, service: UserService = Depends(UserService)):
    return await service.register(user_data)


@router.post("/login/", summary="Аутентификация пользователя")
async def auth_user(user_data: SUserAuth, response: Response, service: UserService = Depends(UserService)):
    return await service.authenticate_user(user_data, response=response)


@router.post("/refresh/", summary="Обновление access и refresh токенов")
async def refresh_tokens(request: Request, response: Response, service: UserService = Depends(UserService)):
    access_token = request.cookies.get(settings.ACCESS_TOKEN_NAME)
    if not access_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Access-токен отсутствует")
    return await service.refresh_tokens(access_token, response)


@router.get("/logout/", status_code=status.HTTP_200_OK, summary="Выход пользователя из системы")
async def logout_user(
    response: Response, user: User = Depends(get_current_user), service: UserService = Depends(UserService)
):
    return await service.logout(user.id, response)

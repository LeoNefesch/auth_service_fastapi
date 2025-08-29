from typing import List

from fastapi import APIRouter, Depends

from app.models.user import User
from app.schemas.user import SUserMe
from app.services.users import UserService
from app.utils.dependencies import get_current_admin_user, get_current_user

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me/", summary="Авторизованный пользователь получает данные о себе", response_model=SUserMe)
async def get_me(user_data: User = Depends(get_current_user)):
    return user_data


@router.get("/all_users/", summary="Только админ может получить список пользователей", response_model=List[SUserMe])
async def get_all_users(user: User = Depends(get_current_admin_user), service: UserService = Depends(UserService)):
    return await service.get_all_users()

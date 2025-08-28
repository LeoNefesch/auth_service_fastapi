from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyCookie

from app.config.main import settings
from app.models.user import User
from app.repositories.user import UsersRepo
from app.utils.security import decode_token

cookie_scheme = APIKeyCookie(name=settings.ACCESS_TOKEN_NAME, auto_error=True)


async def get_current_user(token: str = Depends(cookie_scheme)):
    payload = await decode_token(token)
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Не найден ID пользователя")
    user = await UsersRepo().find_one_or_none(id=user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Пользователь не найден")
    return user


async def get_current_admin_user(current_user: User = Depends(get_current_user)):
    if current_user.is_admin:
        return current_user
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Недостаточно прав!")

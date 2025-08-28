import uuid

from fastapi import HTTPException, Response, status

from app.config.main import settings
from app.config.redis import redis_for_auth
from app.exceptions.users import UserAlreadyExistsError
from app.repositories.user import UsersRepo
from app.schemas.user import SUserAuth, SUserRegister
from app.utils.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_password_hash,
    verify_password,
)


class UserService:
    def __init__(self):
        self.users_repo = UsersRepo()
        self.redis = redis_for_auth

    async def register(self, user_data: SUserRegister):
        """Регистрация пользователя в системе. Создаётся запись в БД."""
        # TODO добавить подтверждение email
        existing = await self.users_repo.find_one_or_none(email=user_data.email)
        if existing:
            raise UserAlreadyExistsError

        data = user_data.model_dump()
        data["password"] = get_password_hash(user_data.password)
        try:
            await self.users_repo.create(entity_data=data)
            return {"message": f"{data['first_name']} {data['last_name']}, Вы успешно зарегистрированы!"}
        except Exception:
            raise UserAlreadyExistsError

    async def authenticate_user(self, user_data: SUserAuth, response: Response):
        """Аутентификация пользователя по email и password. В результате генерируется пара токенов access и refresh"""
        user = await self.users_repo.find_one_or_none(email=user_data.email)
        if not user or not verify_password(user_data.password, user.password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Неверная почта или пароль")
        access_token = await create_access_token({"sub": str(user.id)})
        refresh_token = await create_refresh_token({"sub": str(user.id)})
        await self.redis.setex(f"refresh:{user.id}", 14 * 24 * 3600, refresh_token)
        response.set_cookie(key=settings.ACCESS_TOKEN_NAME, value=access_token, httponly=True)
        return {"access_token": access_token, "refresh_token": refresh_token}

    async def refresh_tokens(self, expired_access_token: str, response: Response):
        """Обновление пары токенов access и refresh"""
        try:
            payload = await decode_token(expired_access_token, verify_exp=False)
            user_id = payload.get("sub")
            if not user_id:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Некорректный токен")
            stored_refresh = await self.redis.get(f"refresh:{user_id}")
            if not stored_refresh:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh-токен не найден")
            await decode_token(stored_refresh)
            new_access = await create_access_token({"sub": user_id})
            new_refresh = await create_refresh_token({"sub": user_id})
            await self.redis.setex(f"refresh:{user_id}", 14 * 24 * 3600, new_refresh)
            response.set_cookie(key=settings.ACCESS_TOKEN_NAME, value=new_access, httponly=True)
            return {"access_token": new_access, "refresh_token": new_refresh}
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Ошибка при обновлении токенов: {e}")

    async def get_all_users(self):
        users = await self.users_repo.get_all()
        return users or None

    async def logout(self, user_id: uuid.UUID, response: Response):
        await self.redis.delete(f"refresh:{user_id}")
        response.delete_cookie(key=settings.ACCESS_TOKEN_NAME)
        return {"message": "Вы вышли из системы"}

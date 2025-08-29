import uuid

from fastapi import BackgroundTasks, HTTPException, Response, status
from fastapi.responses import RedirectResponse

from app.config.main import settings
from app.config.redis import redis_for_auth
from app.exceptions.users import UserAlreadyExistsError
from app.repositories.user import UsersRepo
from app.schemas.user import SUserAuth, SUserRegister, SUserUpdate
from app.utils.email import send_email
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

    async def register(self, user_data: SUserRegister, background_tasks: BackgroundTasks):
        """Регистрация пользователя в системе. Создаётся запись в БД."""
        existing = await self.users_repo.find_one_or_none(email=user_data.email)
        if existing:
            raise UserAlreadyExistsError

        data = user_data.model_dump()
        data["password"] = get_password_hash(user_data.password)
        user = await self.users_repo.create(entity_data=data)
        confirm_token = str(uuid.uuid4())
        await self.redis.setex(f"confirm:{confirm_token}", settings.CONFIRM_TOKEN_EXPIRE_SECONDS, str(user.id))

        confirm_url = f"{settings.DOMAIN}/auth/confirm?token={confirm_token}"
        email_body = f"""
                <h3>Здравствуйте, {user.first_name}!</h3>
                <p>Для подтверждения регистрации перейдите по ссылке:</p>
                <a href="{confirm_url}">Подтвердить email</a>
                """
        background_tasks.add_task(send_email, user.email, "Подтверждение регистрации", email_body)

        return {
            "message": f"{data['first_name']} {data['last_name']}, письмо с подтверждением отправлено на вашу почту"
        }

    async def authenticate_user(self, user_data: SUserAuth, response: Response):
        """Аутентификация пользователя по email и password. В результате генерируется пара токенов access и refresh"""
        user = await self.users_repo.find_one_or_none(email=user_data.email)
        if not user or not verify_password(user_data.password, user.password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Неверная почта или пароль")
        if not user.is_active:
            raise HTTPException(status_code=403, detail="Email не подтвержден")
        access_token = await create_access_token({"sub": str(user.id)})
        refresh_token = await create_refresh_token({"sub": str(user.id)})
        await self.redis.setex(f"refresh:{user.id}", settings.REFRESH_TOKEN_EXPIRE_SECONDS, refresh_token)
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
            await self.redis.setex(f"refresh:{user_id}", settings.REFRESH_TOKEN_EXPIRE_SECONDS, new_refresh)
            response.set_cookie(key=settings.ACCESS_TOKEN_NAME, value=new_access, httponly=True)
            return {"access_token": new_access, "refresh_token": new_refresh}
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Ошибка при обновлении токенов: {e}")

    async def get_all_users(self):
        users = await self.users_repo.get_all()
        return users or None

    async def update_user(self, user_id: int, user_data: SUserUpdate):
        user = await self.users_repo.find_one_or_none(id=user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Пользователь не найден")
        updates = user_data.model_dump(exclude_unset=True)
        updated_user = await self.users_repo.update(user, updates)
        return updated_user

    async def confirm_email(self, token: str) -> RedirectResponse:
        user_id = await self.redis.get(f"confirm:{token}")
        if not user_id:
            raise HTTPException(status_code=400, detail="Неверный или просроченный токен")
        user = await self.users_repo.find_one_or_none(id=user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Пользователь не найден")
        await self.update_user(user.id, SUserUpdate(is_active=True))
        await self.redis.delete(f"confirm:{token}")
        return RedirectResponse(url=f"{settings.DOMAIN}/{settings.REDIRECT_URL}", status_code=302)

    async def logout(self, user_id: uuid.UUID, response: Response):
        await self.redis.delete(f"refresh:{user_id}")
        response.delete_cookie(key=settings.ACCESS_TOKEN_NAME)
        return {"message": "Вы вышли из системы"}

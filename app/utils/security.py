from datetime import UTC, datetime, timedelta

import jwt
from fastapi import HTTPException, status
from passlib.context import CryptContext

from app.config.main import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


async def create_token(data: dict, expires_delta: timedelta, secret_key: str = settings.SECRET_KEY) -> str:
    to_encode = data.copy()
    expire = datetime.now(UTC) + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, secret_key, algorithm=settings.ALGORITHM)


async def create_access_token(data: dict) -> str:
    return await create_token(data, timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))


async def create_refresh_token(data: dict) -> str:
    return await create_token(data, timedelta(days=14))


async def decode_token(token: str, secret_key: str = settings.SECRET_KEY, verify_exp: bool = True) -> dict:
    try:
        return jwt.decode(
            jwt=token, key=secret_key, algorithms=[settings.ALGORITHM], options={"verify_exp": verify_exp}
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Токен истёк")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Токен невалиден")

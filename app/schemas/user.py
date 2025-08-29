import re
import uuid

from pydantic import BaseModel, EmailStr, Field, field_validator


class SUserRegister(BaseModel):
    email: EmailStr
    password: str
    phone: str = Field(..., description="Номер телефона в международном формате, начинающийся с '+'")
    first_name: str
    last_name: str

    @field_validator("phone")
    @classmethod
    def validate_phone_number(cls, value: str) -> str:
        if not re.match(r"^\+\d{5,15}$", value):
            raise ValueError('Номер телефона должен начинаться с "+" и содержать от 5 до 15 цифр')
        return value

    model_config = {
        "json_schema_extra": {
            "example": {
                "email": "user@example.com",
                "password": "password",
                "phone": "+7322222222",
                "first_name": "Иван",
                "last_name": "Иванов",
            }
        }
    }


class SUserAuth(BaseModel):
    email: EmailStr
    password: str

    model_config = {
        "json_schema_extra": {
            "example": {
                "email": "user@example.com",
                "password": "password",
            }
        }
    }


class SUserMe(BaseModel):
    id: uuid.UUID
    email: EmailStr
    password: str
    phone: str
    first_name: str
    last_name: str
    is_user: bool
    is_active: bool
    is_admin: bool

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "f6f40712-663d-461d-a2a5-edf3606bb5e6",
                "email": "user@example.com",
                "password": "password",
                "phone": "+7322222222",
                "first_name": "Иван",
                "last_name": "Иванов",
                "is_user": True,
                "is_active": True,
                "is_admin": False,
            }
        }
    }


class SLoginAnswer(BaseModel):
    access_token: str
    refresh_token: str


class SUserUpdate(BaseModel):
    email: EmailStr | None = None
    phone: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    password: str | None = None
    is_active: bool | None = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "first_name": "Иван",
                "last_name": "Иванов",
                "phone": "+7322222222",
                "is_active": True,
            }
        }
    }

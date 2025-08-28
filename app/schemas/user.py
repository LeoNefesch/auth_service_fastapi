import re

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

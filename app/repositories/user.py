from app.models.user import User
from app.repositories.base import SQLAlchemyRepository


class UsersRepo(SQLAlchemyRepository):
    model = User

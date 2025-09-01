import uuid

from loguru import logger
from sqlalchemy import select

from app.abstractions.base_repository import AbstractRepository
from app.config.database import async_session
from app.exceptions.base import BaseHTTPException


class SQLAlchemyRepository(AbstractRepository):
    model = None

    async def get_all(self):
        async with async_session() as session:
            try:
                query = select(self.model)
                result = await session.execute(query)
                return result.scalars().all()
            except Exception as e:
                logger.error(f"Error: {str(e)}")
                raise BaseHTTPException

    async def create(self, entity_data: dict):
        async with async_session() as session:
            try:
                entity = self.model(**entity_data)
                session.add(entity)
                await session.commit()
                await session.refresh(entity)
                return entity
            except Exception as e:
                await session.rollback()
                logger.error(f"Error: {str(e)}")
                raise BaseHTTPException

    async def find_one_or_none(self, **filter_by):
        async with async_session() as session:
            try:
                query = select(self.model).filter_by(**filter_by)
                result = await session.execute(query)
                return result.scalars().one_or_none()
            except Exception as e:
                logger.error(f"Error: {str(e)}")
                raise BaseHTTPException

    async def update(self, entity: model, updates: dict) -> model:
        """Обновить сущность."""
        async with async_session() as session:
            try:
                for key, value in updates.items():
                    setattr(entity, key, value)
                session.add(entity)
                await session.commit()
                return entity
            except Exception as e:
                logger.error(f"Error: {str(e)}")
                raise BaseHTTPException

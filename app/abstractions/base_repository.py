from abc import ABC, abstractmethod


class AbstractRepository(ABC):
    model = None

    @abstractmethod
    async def create(self, entity_data: dict):
        """Создать сущность."""

    @abstractmethod
    async def find_one_or_none(self, **filter_by) -> model:
        """Получить сущность по фильтру."""

    @abstractmethod
    async def get_all(self, **filter_by) -> list[model]:
        """Вывести список всех сущностей."""

    @abstractmethod
    async def update(self, entity: model, updates: dict) -> model:
        """Обновить сущность."""

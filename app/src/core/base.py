from abc import ABC
from uuid import UUID, uuid4
from typing import Optional


class BaseEntity(ABC):
    """
    Базовый класс для всех сущностей предметной области.
    Содержит общий идентификатор.
    """

    def __init__(self, entity_id: Optional[UUID] = None):
        self._id: UUID = entity_id or uuid4()

    @property
    def id(self) -> UUID:
        return self._id


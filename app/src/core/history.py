from __future__ import annotations

from enum import Enum
from datetime import datetime
from typing import Optional

from core.base import BaseEntity
from core.users import User
from core.tasks import MatchingTask


class RequestStatus(Enum):
    SUCCESS = "success"
    FAILED = "failed"
    PARTIALLY_VALID = "partially_valid"


class PredictionHistoryItem(BaseEntity):
    """
    История запросов и предсказаний (подборов резюме).
    Хранит факт запроса, результат и списанные кредиты.
    """
    def __init__(
        self,
        user: User,
        task: MatchingTask,
        charged_credits: int,
        status: RequestStatus = RequestStatus.SUCCESS,
        invalid_items: Optional[list[str]] = None,
        created_at: Optional[datetime] = None,
    ):
        super().__init__()
        self._user_id = user.id
        self._task_id = task.id
        self._charged_credits = charged_credits
        self._status = status
        self._invalid_items = invalid_items or []
        self._created_at = created_at or datetime.utcnow()

    @property
    def user_id(self):
        return self._user_id

    @property
    def task_id(self):
        return self._task_id

    @property
    def charged_credits(self) -> int:
        return self._charged_credits

    @property
    def status(self) -> RequestStatus:
        return self._status

    def add_invalid_item(self, item: str) -> None:
        self._invalid_items.append(item)

    def is_success(self) -> bool:
        return self._status == RequestStatus.SUCCESS

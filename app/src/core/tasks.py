from core.base import BaseEntity
from core.users import User
from core.queries import JobQuery


class MatchingTask(BaseEntity):
    def __init__(self, user: User, query: JobQuery):
        super().__init__()
        self._user = user
        self._query = query
        self._is_completed = False

    @property
    def user(self) -> User:
        return self._user

    @property
    def query(self) -> JobQuery:
        return self._query

    @property
    def is_completed(self) -> bool:
        return self._is_completed

    def mark_completed(self) -> None:
        self._is_completed = True

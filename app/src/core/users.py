from enum import Enum
from typing import Optional

from core.base import BaseEntity
from core.balance import Balance


class UserRole(Enum):
    EMPLOYER = "employer"
    ADMIN = "admin"


class User(BaseEntity):
    def __init__(self, email: str, role: UserRole, balance: Optional[Balance] = None):
        super().__init__()
        self._email = email
        self._role = role
        self._balance = balance or Balance(0)

    @property
    def balance(self) -> Balance:
        return self._balance

    def can_spend(self, amount: int) -> bool:
        return self._balance.can_spend(amount)

    def spend(self, amount: int) -> None:
        self._balance.spend(amount)

    def top_up(self, amount: int) -> None:
        self._balance.top_up(amount)


class Admin(User):
    def __init__(self, email: str):
        super().__init__(email=email, role=UserRole.ADMIN)

    def top_up_user(self, user: User, amount: int) -> None:
        user.top_up(amount)

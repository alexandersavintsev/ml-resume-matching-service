from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from datetime import datetime
from typing import Optional

from core.base import BaseEntity
from core.users import User


class TransactionType(Enum):
    TOP_UP = "top_up"      # пополнение
    CHARGE = "charge"      # списание


@dataclass(frozen=True)
class Money:
    credits: int

    def __post_init__(self) -> None:
        if self.credits <= 0:
            raise ValueError("credits must be positive")


class Transaction(BaseEntity):
    def __init__(
        self,
        user: User,
        tx_type: TransactionType,
        amount: Money,
        task_id: Optional[str] = None,
        created_at: Optional[datetime] = None,
    ):
        super().__init__()
        self._user_id = user.id
        self._type = tx_type
        self._amount = amount
        self._task_id = task_id
        self._created_at = created_at or datetime.utcnow()

    @property
    def user_id(self):
        return self._user_id

    @property
    def type(self) -> TransactionType:
        return self._type

    @property
    def amount(self) -> Money:
        return self._amount

    def apply(self, user: User) -> None:
        if user.id != self._user_id:
            raise ValueError("Transaction does not belong to this user")

        if self._type == TransactionType.TOP_UP:
            user.top_up(self._amount.credits)
        elif self._type == TransactionType.CHARGE:
            user.spend(self._amount.credits)
        else:
            raise ValueError("Unknown transaction type")

from __future__ import annotations

import uuid
from sqlalchemy import select
from sqlalchemy.orm import Session

from infra.db.models import MatchingTaskORM, PredictionHistoryORM, RequestStatusEnum

def _tx(session: Session):
    tx = session.get_transaction()

    # Если транзакция появилась из-за SQLAlchemy autobegin (например после SELECT),
    # сбрасываем её, чтобы service-операция могла открыть свою транзакцию и закоммититься.
    if tx is not None and getattr(tx, "origin", None) is not None and tx.origin.name == "AUTOBEGIN":
        session.rollback()

    return session.begin_nested() if session.in_transaction() else session.begin()
    

def create_task(session: Session, *, user_id: uuid.UUID, keywords: list[str]) -> uuid.UUID:
    with _tx(session):
        task = MatchingTaskORM(user_id=user_id, keywords=keywords, is_completed=0)
        session.add(task)
        session.flush()
        return task.id


def mark_task_completed(session: Session, *, task_id: uuid.UUID) -> None:
    with _tx(session):
        task = session.get(MatchingTaskORM, task_id)
        if not task:
            raise ValueError("task not found")
        task.is_completed = 1


def add_history_item(
    session: Session,
    *,
    user_id: uuid.UUID,
    task_id: uuid.UUID,
    charged_credits: int,
    status: RequestStatusEnum,
    invalid_items: list[str] | None = None,
) -> uuid.UUID:
    with _tx(session):
        item = PredictionHistoryORM(
            user_id=user_id,
            task_id=task_id,
            charged_credits=charged_credits,
            status=status,
            invalid_items=invalid_items or [],
        )
        session.add(item)
        session.flush()
        return item.id


def list_history(session: Session, *, user_id: uuid.UUID) -> list[PredictionHistoryORM]:
    q = (
        select(PredictionHistoryORM)
        .where(PredictionHistoryORM.user_id == user_id)
        .order_by(PredictionHistoryORM.created_at.desc())
    )
    return list(session.scalars(q).all())

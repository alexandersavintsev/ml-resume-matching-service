from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.deps import db_session, get_current_user
from api.schemas import TransactionOut, PredictionHistoryOut

from infra.db.models import UserORM
from services.wallet_service import list_transactions
from services.history_service import list_history


router = APIRouter(prefix="/history", tags=["history"])


@router.get("/transactions", response_model=list[TransactionOut])
def transactions(
    user: UserORM = Depends(get_current_user),
    session: Session = Depends(db_session),
) -> list[TransactionOut]:
    txs = list_transactions(session, user_id=user.id)
    return [
        TransactionOut(
            id=tx.id,
            tx_type=tx.tx_type.value,
            amount_credits=tx.amount_credits,
            task_id=tx.task_id,
            created_at=tx.created_at,
        )
        for tx in txs
    ]


@router.get("/predictions", response_model=list[PredictionHistoryOut])
def predictions(
    user: UserORM = Depends(get_current_user),
    session: Session = Depends(db_session),
) -> list[PredictionHistoryOut]:
    hist = list_history(session, user_id=user.id)
    return [
        PredictionHistoryOut(
            id=h.id,
            task_id=h.task_id,
            charged_credits=h.charged_credits,
            status=h.status.value,
            invalid_items=h.invalid_items,
            created_at=h.created_at,
        )
        for h in hist
    ]

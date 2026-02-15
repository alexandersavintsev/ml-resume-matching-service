from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.deps import db_session, get_current_user
from api.schemas import BalanceResponse, TopUpRequest, TxResponse

from infra.db.models import BalanceORM, UserORM
from services.wallet_service import top_up


router = APIRouter(prefix="/balance", tags=["balance"])


@router.get("", response_model=BalanceResponse)
def get_balance(
    user: UserORM = Depends(get_current_user),
    session: Session = Depends(db_session),
) -> BalanceResponse:
    bal = session.get(BalanceORM, user.id)
    credits = bal.credits if bal else 0
    return BalanceResponse(user_id=user.id, credits=credits)


@router.post("/top-up", response_model=TxResponse)
def topup(
    payload: TopUpRequest,
    user: UserORM = Depends(get_current_user),
    session: Session = Depends(db_session),
) -> TxResponse:
    res = top_up(session, user_id=user.id, amount=payload.amount)
    return TxResponse(tx_id=res.tx_id, new_balance=res.new_balance)

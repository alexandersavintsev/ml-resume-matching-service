from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.deps import db_session, get_current_user
from api.errors import bad_request, insufficient_balance
from api.schemas import PredictRequest, PredictResponse, PredictItem

from infra.db.models import BalanceORM, RequestStatusEnum, UserORM
from services.history_service import create_task, add_history_item, mark_task_completed
from services.wallet_service import charge, InsufficientBalanceError


router = APIRouter(prefix="/predict", tags=["predict"])


def _score_resume(keywords: list[str], resume_text: str) -> float:
    # Простой baseline: доля совпавших ключевых слов (case-insensitive)
    text = resume_text.lower()
    if not text.strip():
        return 0.0
    hits = sum(1 for k in keywords if k.lower() in text)
    return hits / max(len(keywords), 1)


@router.post("", response_model=PredictResponse)
def predict(
    payload: PredictRequest,
    user: UserORM = Depends(get_current_user),
    session: Session = Depends(db_session),
) -> PredictResponse:
    # 1) валидация данных: фиксируем "invalid_items" без дублирования бизнес-логики
    invalid: list[str] = []
    cleaned_resumes: list[str] = []
    for i, r in enumerate(payload.resumes):
        if not isinstance(r, str) or not r.strip():
            invalid.append(f"resumes[{i}]")
        else:
            cleaned_resumes.append(r)

    if not cleaned_resumes:
        raise bad_request("INVALID_INPUT", "All resumes are empty/invalid", {"invalid_items": invalid})

    # 2) создаём ML-task (в БД)
    task_id = create_task(session, user_id=user.id, keywords=payload.keywords)

    # 3) списываем кредиты (через service)
    bal = session.get(BalanceORM, user.id)
    current_credits = bal.credits if bal else 0

    try:
        charge(session, user_id=user.id, amount=payload.cost_credits, task_id=task_id)
    except InsufficientBalanceError:
        # фиксируем историю FAILED
        add_history_item(
            session,
            user_id=user.id,
            task_id=task_id,
            charged_credits=0,
            status=RequestStatusEnum.FAILED,
            invalid_items=invalid,
        )
        raise insufficient_balance(current=current_credits, required=payload.cost_credits)

    # 4) делаем baseline-предсказание
    scored = [
        (r, _score_resume(payload.keywords, r))
        for r in cleaned_resumes
    ]
    scored.sort(key=lambda x: x[1], reverse=True)
    top = scored[: payload.top_k]

    status = RequestStatusEnum.PARTIALLY_VALID if invalid else RequestStatusEnum.SUCCESS

    # 5) пишем историю + отмечаем задачу выполненной
    add_history_item(
        session,
        user_id=user.id,
        task_id=task_id,
        charged_credits=payload.cost_credits,
        status=status,
        invalid_items=invalid,
    )
    mark_task_completed(session, task_id=task_id)

    return PredictResponse(
        task_id=task_id,
        charged_credits=payload.cost_credits,
        status=status.value,
        invalid_items=invalid,
        top=[PredictItem(resume_text=r, score=s) for r, s in top],
    )

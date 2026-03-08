

from __future__ import annotations

import re
from functools import lru_cache
from pymorphy3 import MorphAnalyzer

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.deps import db_session, get_current_user
from api.errors import bad_request, insufficient_balance
from api.schemas import PredictRequest, PredictResponse, PredictItem

from infra.db.models import BalanceORM, RequestStatusEnum, UserORM
from services.history_service import create_task, add_history_item, mark_task_completed
from services.wallet_service import charge, InsufficientBalanceError


router = APIRouter(prefix="/predict", tags=["predict"])

TOKEN_RE = re.compile(r"[A-Za-zА-Яа-яЁё0-9]+")

@lru_cache(maxsize=1)
def get_morph() -> MorphAnalyzer:
    return MorphAnalyzer()


def normalize_token(token: str) -> str:
    token = token.strip().lower()
    if not token:
        return token

    # Русские слова нормализуем через pymorphy3
    if re.search(r"[а-яё]", token):
        try:
            return get_morph().normal_forms(token)[0]
        except Exception:
            return token

    # Английские оставляем как есть
    return token


def normalize_text(text: str) -> set[str]:
    tokens = TOKEN_RE.findall(text.lower())
    return {normalize_token(t) for t in tokens if t.strip()}


def _score_resume(keywords: list[str], resume_text: str) -> float:
    if not resume_text.strip():
        return 0.0

    normalized_keywords = [normalize_token(k) for k in keywords if k.strip()]
    if not normalized_keywords:
        return 0.0

    resume_tokens = normalize_text(resume_text)

    hits = sum(1 for k in normalized_keywords if k in resume_tokens)
    return hits / len(normalized_keywords)

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

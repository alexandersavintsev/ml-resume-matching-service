from __future__ import annotations

import uuid
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from api.deps import TOKENS, db_session
from api.errors import conflict, not_found
from api.schemas import RegisterRequest, RegisterResponse, LoginRequest, LoginResponse

from infra.db.models import UserORM, UserRoleEnum
from services.wallet_service import create_user


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=RegisterResponse)
def register(payload: RegisterRequest, session: Session = Depends(db_session)) -> RegisterResponse:
    # idempotent create_user already returns existing id if email exists
    role = UserRoleEnum.ADMIN if payload.role == "admin" else UserRoleEnum.EMPLOYER
    user_id = create_user(session, email=str(payload.email), role=role, initial_credits=payload.initial_credits)

    user = session.get(UserORM, user_id)
    if not user:
        raise not_found("user not found after creation")

    return RegisterResponse(user_id=user.id, email=user.email, role=user.role.value)


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest, session: Session = Depends(db_session)) -> LoginResponse:
    user = session.scalar(select(UserORM).where(UserORM.email == str(payload.email)))
    if not user:
        raise not_found("user not found")

    token = str(uuid.uuid4())
    TOKENS[token] = user.id
    return LoginResponse(token=token)

from __future__ import annotations

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


# ---- Auth ----
class RegisterRequest(BaseModel):
    email: EmailStr
    role: Literal["employer", "admin"] = "employer"
    initial_credits: int = Field(default=0, ge=0, le=1_000_000)


class RegisterResponse(BaseModel):
    user_id: UUID
    email: EmailStr
    role: str


class LoginRequest(BaseModel):
    email: EmailStr


class LoginResponse(BaseModel):
    token: str
    token_type: str = "bearer"


# ---- Balance ----
class BalanceResponse(BaseModel):
    user_id: UUID
    credits: int


class TopUpRequest(BaseModel):
    amount: int = Field(..., ge=1, le=1_000_000)


class TxResponse(BaseModel):
    tx_id: UUID
    new_balance: int


# ---- Predict ----
class PredictRequest(BaseModel):
    keywords: list[str] = Field(..., min_length=1, max_length=50)
    resumes: list[str] = Field(..., min_length=1, max_length=200)
    top_k: int = Field(default=5, ge=1, le=50)
    cost_credits: int = Field(default=10, ge=1, le=10_000)


class PredictItem(BaseModel):
    resume_text: str
    score: float


class PredictResponse(BaseModel):
    task_id: UUID
    charged_credits: int
    status: str
    invalid_items: list[str] = []
    top: list[PredictItem]


# ---- History ----
class TransactionOut(BaseModel):
    id: UUID
    tx_type: str
    amount_credits: int
    task_id: UUID | None
    created_at: datetime


class PredictionHistoryOut(BaseModel):
    id: UUID
    task_id: UUID
    charged_credits: int
    status: str
    invalid_items: list[str]
    created_at: datetime

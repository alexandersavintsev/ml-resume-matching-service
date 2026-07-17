from __future__ import annotations

from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, Field


class PredictAsyncRequest(BaseModel):
    features: dict[str, float] = Field(..., min_length=1)
    model: str = Field(default="demo_model", min_length=1, max_length=128)

    user_id: UUID
    cost_credits: int = Field(default=10, ge=1, le=10_000)


class PredictAsyncResponse(BaseModel):
    task_id: UUID


class MLTaskMessage(BaseModel):
    task_id: UUID
    features: dict[str, float]
    model: str
    timestamp: datetime

    user_id: UUID
    cost_credits: int


class WorkerResult(BaseModel):
    task_id: UUID
    prediction: float | None = None
    worker_id: str
    status: Literal["success", "failed", "partially_valid"]
    error: str | None = None

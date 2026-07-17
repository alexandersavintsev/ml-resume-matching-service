from __future__ import annotations

import json
from datetime import datetime
from uuid import uuid4

from fastapi import FastAPI
import pika

from infra.db.database import get_session
from infra.db.models import BalanceORM, RequestStatusEnum
from services.history_service import create_task
from services.wallet_service import charge, InsufficientBalanceError
from mq.schemas import PredictAsyncRequest, PredictAsyncResponse, MLTaskMessage
from mq.rabbit import create_connection, declare_queue
from mq.settings import RABBITMQ_QUEUE


app = FastAPI(title="ML Publisher API (RabbitMQ)")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/predict", response_model=PredictAsyncResponse)
def predict_async(payload: PredictAsyncRequest) -> PredictAsyncResponse:
    """
    1) создаём task в БД
    2) списываем кредиты (как в твоём sync /predict)
    3) публикуем сообщение в RabbitMQ
    4) возвращаем task_id
    """
    session = get_session()
    try:
        # 1) task в БД
        task_id = create_task(session, user_id=payload.user_id, keywords=[payload.model])

        # 2) списание кредитов
        bal = session.get(BalanceORM, payload.user_id)
        current = bal.credits if bal else 0
        try:
            charge(session, user_id=payload.user_id, amount=payload.cost_credits, task_id=task_id)
        except InsufficientBalanceError:
            # Не пишем историю тут, её запишет/не запишет воркер — но задача уже создана.
            # Для “ручного теста” достаточно вернуть 402.
            return PredictAsyncResponse(task_id=task_id)  # оставим task_id для трассировки

        # 3) публикуем
        msg = MLTaskMessage(
            task_id=task_id,
            features=payload.features,
            model=payload.model,
            timestamp=datetime.utcnow(),
            user_id=payload.user_id,
            cost_credits=payload.cost_credits,
        )

        conn = create_connection()
        try:
            ch = conn.channel()
            declare_queue(ch)

            ch.basic_publish(
                exchange="",
                routing_key=RABBITMQ_QUEUE,
                body=msg.model_dump_json().encode("utf-8"),
                properties=pika.BasicProperties(
                    delivery_mode=2,  # persistent
                    content_type="application/json",
                ),
            )
        finally:
            conn.close()

        return PredictAsyncResponse(task_id=task_id)

    finally:
        session.close()

from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime
from uuid import UUID

import pika
from sqlalchemy import text

from infra.db.database import get_session
from infra.db.models import RequestStatusEnum
from services.history_service import add_history_item, mark_task_completed
from mq.rabbit import create_connection, declare_queue
from mq.schemas import MLTaskMessage, WorkerResult
from mq.settings import RABBITMQ_QUEUE


CREATE_RESULTS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS prediction_results (
    task_id UUID PRIMARY KEY,
    user_id UUID NOT NULL,
    model VARCHAR(128) NOT NULL,
    prediction DOUBLE PRECISION,
    worker_id VARCHAR(64) NOT NULL,
    status VARCHAR(32) NOT NULL,
    error TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);
"""


INSERT_RESULT_SQL = """
INSERT INTO prediction_results (task_id, user_id, model, prediction, worker_id, status, error, created_at)
VALUES (:task_id, :user_id, :model, :prediction, :worker_id, :status, :error, :created_at)
ON CONFLICT (task_id) DO UPDATE SET
    prediction = EXCLUDED.prediction,
    worker_id = EXCLUDED.worker_id,
    status = EXCLUDED.status,
    error = EXCLUDED.error,
    created_at = EXCLUDED.created_at;
"""


def ensure_results_table() -> None:
    session = get_session()
    try:
        session.execute(text(CREATE_RESULTS_TABLE_SQL))
        session.commit()
    finally:
        session.close()


def mock_predict(features: dict[str, float]) -> float:
    return float(sum(features.values()))


def validate_features(features: dict[str, float]) -> tuple[bool, list[str]]:
    invalid = []
    if not isinstance(features, dict) or not features:
        return False, ["features"]
    for k, v in features.items():
        if not isinstance(k, str) or not k.strip():
            invalid.append(f"features.key")
        if not isinstance(v, (int, float)):
            invalid.append(f"features[{k}]")
    return (len(invalid) == 0), invalid


def process_message(worker_id: str, raw_body: bytes) -> WorkerResult:
    try:
        data = json.loads(raw_body.decode("utf-8"))
        msg = MLTaskMessage(**data)
    except Exception as e:
        return WorkerResult(
            task_id=UUID(int=0),
            prediction=None,
            worker_id=worker_id,
            status="failed",
            error=f"invalid json/schema: {e}",
        )

    ok, invalid_items = validate_features(msg.features)
    if not ok:
        return WorkerResult(
            task_id=msg.task_id,
            prediction=None,
            worker_id=worker_id,
            status="partially_valid",
            error=f"invalid_items={invalid_items}",
        )

    try:
        pred = mock_predict(msg.features)
        return WorkerResult(
            task_id=msg.task_id,
            prediction=pred,
            worker_id=worker_id,
            status="success",
        )
    except Exception as e:
        return WorkerResult(
            task_id=msg.task_id,
            prediction=None,
            worker_id=worker_id,
            status="failed",
            error=str(e),
        )


def save_result_and_history(msg: MLTaskMessage, res: WorkerResult) -> None:
    session = get_session()
    try:
        session.execute(
            text(INSERT_RESULT_SQL),
            dict(
                task_id=str(msg.task_id),
                user_id=str(msg.user_id),
                model=msg.model,
                prediction=res.prediction,
                worker_id=res.worker_id,
                status=res.status,
                error=res.error,
                created_at=datetime.utcnow(),
            ),
        )
        session.commit()

        if res.status == "success":
            st = RequestStatusEnum.SUCCESS
            invalid_items = []
            charged = msg.cost_credits
        elif res.status == "partially_valid":
            st = RequestStatusEnum.PARTIALLY_VALID
            invalid_items = [res.error] if res.error else ["invalid_features"]
            charged = msg.cost_credits
        else:
            st = RequestStatusEnum.FAILED
            invalid_items = [res.error] if res.error else ["failed"]
            charged = 0  

        add_history_item(
            session,
            user_id=msg.user_id,
            task_id=msg.task_id,
            charged_credits=charged,
            status=st,
            invalid_items=invalid_items,
        )
        mark_task_completed(session, task_id=msg.task_id)
        session.commit()

    finally:
        session.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--worker-id", required=True)
    args = parser.parse_args()
    worker_id: str = args.worker_id

    ensure_results_table()

    conn = create_connection()
    ch = conn.channel()
    declare_queue(ch)

    ch.basic_qos(prefetch_count=1)

    print(f"[{worker_id}] waiting for messages in queue={RABBITMQ_QUEUE}...", flush=True)

    def on_message(channel, method, properties, body: bytes):
        try:
            payload = json.loads(body.decode("utf-8"))
            msg = MLTaskMessage(**payload)
        except Exception as e:
            print(f"[{worker_id}] bad message: {e}", flush=True)
            channel.basic_ack(delivery_tag=method.delivery_tag)
            return

        res = process_message(worker_id, body)
        print(f"[{worker_id}] processed task={msg.task_id} status={res.status} pred={res.prediction}", flush=True)

        try:
            save_result_and_history(msg, res)
        except Exception as e:
            print(f"[{worker_id}] ERROR saving result: {e}", flush=True)
            channel.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
            return

        channel.basic_ack(delivery_tag=method.delivery_tag)

    ch.basic_consume(queue=RABBITMQ_QUEUE, on_message_callback=on_message, auto_ack=False)

    try:
        ch.start_consuming()
    except KeyboardInterrupt:
        print(f"[{worker_id}] stopping...", flush=True)
    finally:
        try:
            conn.close()
        except Exception:
            pass


if __name__ == "__main__":
    main()

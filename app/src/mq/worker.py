from __future__ import annotations

import argparse
import json
from datetime import datetime
import numpy as np
from sklearn.linear_model import LinearRegression

from infra.db.database import get_session
from infra.db.models import RequestStatusEnum

from services.history_service import add_history_item, mark_task_completed
from mq.rabbit import create_connection, declare_queue
from mq.schemas import MLTaskMessage, WorkerResult
from mq.settings import RABBITMQ_QUEUE

from sqlalchemy.exc import IntegrityError
from infra.db.database import engine
from infra.db.prediction_results_model import PredictionResultORM


class DemoSklearnModel:
    def __init__(self) -> None:
        # синтетические данные — но модель реально обучается (fit) и реально предсказывает (predict)
        X = np.array([
            [0.0, 0.0],
            [1.0, 1.0],
            [10.0, 0.5],
            [3.3, 4.4],
            [1.2, 5.7],
        ], dtype=float)
        y = np.array([0.0, 2.0, 10.5, 7.7, 6.9], dtype=float)
        self._model = LinearRegression().fit(X, y)

    def predict(self, x1: float, x2: float) -> float:
        pred = self._model.predict(np.array([[x1, x2]], dtype=float))[0]
        return float(pred)


def ensure_results_table() -> None:
    try:
        # создаём только таблицу prediction_results, не трогаем остальную метадату
        PredictionResultORM.__table__.create(bind=engine, checkfirst=True)
    except IntegrityError:
        # гонка старта двух воркеров — второй может поймать уникальность системного типа
        # просто продолжаем: таблица уже создана
        pass


def validate_features(features: dict[str, float]) -> tuple[bool, list[str]]:
    invalid = []
    if not isinstance(features, dict):
        return False, ["features"]

    for key in ("x1", "x2"):
        if key not in features:
            invalid.append(f"features.{key}")

    for k, v in features.items():
        if not isinstance(v, (int, float)):
            invalid.append(f"features[{k}]")

    return (len(invalid) == 0), invalid
    

def process_message(worker_id: str, msg: MLTaskMessage, ml_model: DemoSklearnModel) -> WorkerResult:

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
        x1 = float(msg.features["x1"])
        x2 = float(msg.features["x2"])
        pred = ml_model.predict(x1, x2)

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
        # --- ORM upsert по task_id ---
        row = session.get(PredictionResultORM, msg.task_id)
        if row is None:
            row = PredictionResultORM(
                task_id=msg.task_id,
                user_id=msg.user_id,
                model=msg.model,
                prediction=res.prediction,
                worker_id=res.worker_id,
                status=res.status,
                error=res.error,
                created_at=datetime.utcnow(),
            )
            session.add(row)
        else:
            row.user_id = msg.user_id
            row.model = msg.model
            row.prediction = res.prediction
            row.worker_id = res.worker_id
            row.status = res.status
            row.error = res.error
            row.created_at = datetime.utcnow()

        session.commit()

        # --- история / завершение task ---
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

    ml_model = DemoSklearnModel()

    def on_message(channel, method, properties, body: bytes):
        try:
            payload = json.loads(body.decode("utf-8"))
            msg = MLTaskMessage(**payload)
        except Exception as e:
            print(f"[{worker_id}] bad message: {e}", flush=True)
            channel.basic_ack(delivery_tag=method.delivery_tag)
            return

        res = process_message(worker_id, msg, ml_model)
        print(f"[{worker_id}] processed task={res.task_id} status={res.status} pred={res.prediction}", flush=True)

        try:
            # save uses msg for history links (user_id/task_id/cost_credits/model)
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


import os
import time
import pika


def create_connection():
    host = os.getenv("RABBITMQ_HOST", "rabbitmq")
    port = int(os.getenv("RABBITMQ_PORT", "5672"))
    user = os.getenv("RABBITMQ_USER", "guest")
    password = os.getenv("RABBITMQ_PASSWORD", "guest")

    creds = pika.PlainCredentials(user, password)

    params = pika.ConnectionParameters(
        host=host,
        port=port,
        credentials=creds,
        heartbeat=30,
        blocked_connection_timeout=30,
        connection_attempts=1,   # retries делаем сами
        socket_timeout=5,
    )

    last_err = None

    # retry loop — ждём пока rabbitmq реально поднимется
    for _ in range(20):
        try:
            return pika.BlockingConnection(params)
        except Exception as e:
            last_err = e
            time.sleep(2)

    raise last_err


def declare_queue(channel):
    queue_name = os.getenv("RABBITMQ_QUEUE", "ml_tasks")

    channel.queue_declare(
        queue=queue_name,
        durable=True,
    )


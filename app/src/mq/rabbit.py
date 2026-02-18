from __future__ import annotations

import pika

from mq.settings import (
    RABBITMQ_HOST,
    RABBITMQ_PORT,
    RABBITMQ_USER,
    RABBITMQ_PASSWORD,
    RABBITMQ_QUEUE,
)


def create_connection() -> pika.BlockingConnection:
    creds = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASSWORD)
    params = pika.ConnectionParameters(
        host=RABBITMQ_HOST,
        port=RABBITMQ_PORT,
        credentials=creds,
        heartbeat=30,
        blocked_connection_timeout=30,
    )
    return pika.BlockingConnection(params)


def declare_queue(channel: pika.channel.Channel) -> None:
    # durable=True чтобы сообщения переживали рестарт брокера (при persistent publish)
    channel.queue_declare(queue=RABBITMQ_QUEUE, durable=True)

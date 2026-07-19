import os


def env(name: str, default: str) -> str:
    return os.getenv(name, default)


RABBITMQ_HOST = env("RABBITMQ_HOST", "rabbitmq")
RABBITMQ_PORT = int(env("RABBITMQ_PORT", "5672"))
RABBITMQ_USER = env("RABBITMQ_USER", "guest")
RABBITMQ_PASSWORD = env("RABBITMQ_PASSWORD", "guest")
RABBITMQ_QUEUE = env("RABBITMQ_QUEUE", "ml_tasks")

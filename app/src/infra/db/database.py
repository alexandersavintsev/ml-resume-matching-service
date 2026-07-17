import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase


def get_database_url() -> str:
    url = os.getenv("DATABASE_URL")
    if url:
        return url

    # fallback from separate vars (optional)
    db = os.getenv("POSTGRES_DB", "ml_service")
    user = os.getenv("POSTGRES_USER", "ml_user")
    pwd = os.getenv("POSTGRES_PASSWORD", "ml_password")
    host = os.getenv("POSTGRES_HOST", "database")
    port = os.getenv("POSTGRES_PORT", "5432")
    return f"postgresql+psycopg://{user}:{pwd}@{host}:{port}/{db}"


class Base(DeclarativeBase):
    pass


engine = create_engine(get_database_url(), pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_session():
    return SessionLocal()

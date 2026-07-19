from __future__ import annotations

import uuid
from typing import Generator

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from infra.db.database import get_session
from infra.db.models import UserORM

from api.errors import unauthorized, not_found


# ---- DB session dependency (не меняем infra/db/database.py) ----
def db_session() -> Generator[Session, None, None]:
    session = get_session()
    try:
        yield session
    finally:
        session.close()


# ---- Very basic in-memory token auth (учебная) ----
_bearer = HTTPBearer(auto_error=False)
TOKENS: dict[str, uuid.UUID] = {}  # token -> user_id


def get_current_user(
    creds: HTTPAuthorizationCredentials | None = Depends(_bearer),
    session: Session = Depends(db_session),
) -> UserORM:
    if creds is None or creds.scheme.lower() != "bearer":
        raise unauthorized("Missing bearer token")

    token = creds.credentials
    user_id = TOKENS.get(token)
    if not user_id:
        raise unauthorized("Invalid token")

    user = session.get(UserORM, user_id)
    if not user:
        raise not_found("user not found")

    return user

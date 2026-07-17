from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from infra.db.database import engine, get_session, Base
from infra.db.models import UserRoleEnum, UserORM, BalanceORM, MLModelORM


DEMO_USER_EMAIL = "demo_user@example.com"
DEMO_ADMIN_EMAIL = "demo_admin@example.com"


def create_tables() -> None:
    Base.metadata.create_all(bind=engine)


def init_demo_data() -> None:
    """
    Idempotent initialization:
    - demo user + balance
    - demo admin + balance
    - base ML models
    """
    session = get_session()
    try:
        # demo user
        user = session.scalar(select(UserORM).where(UserORM.email == DEMO_USER_EMAIL))
        if not user:
            user = UserORM(email=DEMO_USER_EMAIL, role=UserRoleEnum.EMPLOYER)
            session.add(user)
            session.flush()  # to get user.id
            session.add(BalanceORM(user_id=user.id, credits=100))

        # demo admin
        admin = session.scalar(select(UserORM).where(UserORM.email == DEMO_ADMIN_EMAIL))
        if not admin:
            admin = UserORM(email=DEMO_ADMIN_EMAIL, role=UserRoleEnum.ADMIN)
            session.add(admin)
            session.flush()
            session.add(BalanceORM(user_id=admin.id, credits=0))

        # base models
        base_models = [
            ("baseline-bm25", "Simple keyword matching / BM25 baseline"),
            ("dummy-bert", "Placeholder transformer-based ranker"),
        ]
        for name, desc in base_models:
            exists = session.scalar(select(MLModelORM).where(MLModelORM.name == name))
            if not exists:
                session.add(MLModelORM(name=name, description=desc))

        session.commit()
    except IntegrityError:
        session.rollback()
        # If concurrent init happens, idempotency still holds.
    finally:
        session.close()


def main():
    create_tables()
    init_demo_data()
    print("DB initialized")


if __name__ == "__main__":
    main()

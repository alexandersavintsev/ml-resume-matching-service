from infra.db.init_db import create_tables, init_demo_data
from infra.db.database import get_session
from infra.db.models import BalanceORM, UserRoleEnum, RequestStatusEnum
from sqlalchemy import select

from services.wallet_service import create_user, top_up, charge, list_transactions
from services.history_service import create_task, add_history_item, list_history


def main():
    create_tables()
    init_demo_data()

    session = get_session()
    try:
        # create user
        user_id = create_user(session, email="test_user@example.com", role=UserRoleEnum.EMPLOYER, initial_credits=10)
        print("Created/loaded user:", user_id)

        # show balance
        bal = session.get(BalanceORM, user_id)
        print("Initial balance:", bal.credits)

        # top up
        r1 = top_up(session, user_id=user_id, amount=50)
        print("Top up tx:", r1.tx_id, "new_balance:", r1.new_balance)

        # create task
        task_id = create_task(session, user_id=user_id, keywords=["python", "fastapi", "sqlalchemy"])
        print("Created task:", task_id)

        # charge credits for task
        r2 = charge(session, user_id=user_id, amount=20, task_id=task_id)
        print("Charge tx:", r2.tx_id, "new_balance:", r2.new_balance)

        # write prediction history
        hist_id = add_history_item(
            session,
            user_id=user_id,
            task_id=task_id,
            charged_credits=20,
            status=RequestStatusEnum.SUCCESS,
            invalid_items=[],
        )
        print("History item:", hist_id)

        # list transactions
        txs = list_transactions(session, user_id=user_id)
        print("\nTransactions:")
        for tx in txs:
            print(tx.created_at, tx.tx_type, tx.amount_credits, tx.task_id)

        # list history
        hist = list_history(session, user_id=user_id)
        print("\nPrediction history:")
        for h in hist:
            print(h.created_at, h.status, h.charged_credits, h.task_id, h.invalid_items)

    finally:
        session.close()


if __name__ == "__main__":
    main()


from fastapi import FastAPI

from api.routers import auth_router, balance_router, predict_router, history_router
from infra.db.init_db import create_tables, init_demo_data

app = FastAPI(title="ML Resume Matching Service")

@app.on_event("startup")
def on_startup() -> None:
    create_tables()
    init_demo_data()

@app.get("/health")
def health():
    return {"status": "ok"}

app.include_router(auth_router)
app.include_router(balance_router)
app.include_router(predict_router)
app.include_router(history_router)

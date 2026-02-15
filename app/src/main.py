from fastapi import FastAPI

from api.routers import auth_router, balance_router, predict_router, history_router

app = FastAPI(title="ML Resume Matching Service")

@app.get("/health")
def health():
    return {"status": "ok"}

# --- include routers ---
app.include_router(auth_router)
app.include_router(balance_router)
app.include_router(predict_router)
app.include_router(history_router)

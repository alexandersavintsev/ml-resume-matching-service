from .auth import router as auth_router
from .balance import router as balance_router
from .predict import router as predict_router
from .history import router as history_router

__all__ = ["auth_router", "balance_router", "predict_router", "history_router"]

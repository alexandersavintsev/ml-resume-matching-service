from core.base import BaseEntity
from core.predictions import Prediction
from core.resumes import Resume


class MatchingResult(BaseEntity):
    def __init__(self, predictions: list[Prediction]):
        super().__init__()
        self._predictions = predictions

    def top_k(self, k: int) -> list[Resume]:
        return [
            p.resume
            for p in sorted(self._predictions, key=lambda p: p.score, reverse=True)[:k]
        ]

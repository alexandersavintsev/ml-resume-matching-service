from abc import ABC, abstractmethod

from core.predictions import Prediction
from core.resumes import Resume
from core.queries import JobQuery


class MLModel(ABC):
    @abstractmethod
    def predict(self, query: JobQuery, resumes: list[Resume]) -> list[Prediction]:
        """Returns relevance prediction for each resume."""
        raise NotImplementedError

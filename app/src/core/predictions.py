from dataclasses import dataclass

from core.resumes import Resume


@dataclass(frozen=True)
class Prediction:
    resume: Resume
    score: float

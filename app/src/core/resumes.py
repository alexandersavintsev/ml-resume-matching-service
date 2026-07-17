from core.base import BaseEntity


class Resume(BaseEntity):
    def __init__(self, text: str):
        super().__init__()
        self._text = text

    @property
    def text(self) -> str:
        return self._text

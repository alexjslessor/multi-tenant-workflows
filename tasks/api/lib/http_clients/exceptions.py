
from typing import Any


class HttpxException(Exception):
    def __init__(self, msg: str, error: Any, status_code: int | None = None):
        self.msg = msg
        self.error = error
        self.status_code = status_code

    def __str__(self):
        try:
            return f"{self.msg!s} -> {self.error['error']!s}"
        except TypeError as e:
            return f"{self.msg!s} -> {self.error!s}"
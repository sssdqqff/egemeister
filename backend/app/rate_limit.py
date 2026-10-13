import time
from collections import deque

from app.config import settings


class FailureLimiter:
    def __init__(self, max_failures: int, window_seconds: int):
        self.max_failures = max_failures
        self.window_seconds = window_seconds
        self._failures: dict[str, deque[float]] = {}

    def is_blocked(self, key: str) -> bool:
        failures = self._failures.get(key)
        if not failures:
            return False
        now = time.monotonic()
        while failures and now - failures[0] > self.window_seconds:
            failures.popleft()
        if not failures:
            del self._failures[key]
            return False
        return len(failures) >= self.max_failures

    def register_failure(self, key: str) -> None:
        self._failures.setdefault(key, deque()).append(time.monotonic())


login_limiter = FailureLimiter(settings.login_max_failures, settings.login_failure_window_seconds)
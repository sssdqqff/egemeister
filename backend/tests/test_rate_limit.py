from types import SimpleNamespace

import app.rate_limit as rate_limit
from app.rate_limit import FailureLimiter


def test_failure_limiter_clears_expired_failures(monkeypatch):
    clock = {"now": 100.0}
    monkeypatch.setattr(
        rate_limit,
        "time",
        SimpleNamespace(monotonic=lambda: clock["now"]),
    )

    limiter = FailureLimiter(max_failures=2, window_seconds=10)

    assert not limiter.is_blocked("client")

    limiter.register_failure("client")
    assert not limiter.is_blocked("client")

    clock["now"] = 101.0
    limiter.register_failure("client")
    assert limiter.is_blocked("client")

    clock["now"] = 112.0
    assert not limiter.is_blocked("client")
    assert "client" not in limiter._failures
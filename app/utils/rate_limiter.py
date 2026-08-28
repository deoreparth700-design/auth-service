import time


MAX_ATTEMPTS = 5
WINDOW_SECONDS = 60


_login_attempts: dict[str, list[float]] = {}


def is_rate_limited(key: str) -> bool:
    now = time.time()

    attempts = _login_attempts.get(key, [])

    # Keep only attempts inside the current window
    attempts = [
        timestamp
        for timestamp in attempts
        if now - timestamp < WINDOW_SECONDS
    ]

    _login_attempts[key] = attempts

    return len(attempts) >= MAX_ATTEMPTS


def record_failed_attempt(key: str) -> None:
    now = time.time()

    attempts = _login_attempts.get(key, [])

    attempts = [
        timestamp
        for timestamp in attempts
        if now - timestamp < WINDOW_SECONDS
    ]

    attempts.append(now)

    _login_attempts[key] = attempts


def reset_attempts(key: str) -> None:
    _login_attempts.pop(key, None)
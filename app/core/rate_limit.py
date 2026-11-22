import time
import redis
from fastapi import HTTPException, Request, status
from app.core.redis import redis_client

def check_rate_limit(
        scope: str,
        identifier: str,
        max_requests: int = 5,
        window_seconds: int=60
) -> None:
    window = (time.time()) // window_seconds
    key = f"rf:{scope}:{identifier}:{window}"
    try:
        count = redis_client.incr(key)
        if count == 1:
            redis_client.expire(key, window_seconds)

        if count > max_requests:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many requests",
                headers={"Retry-After": str(window_seconds)},
                )
    except redis.RedisError:
        pass

def login_rate_limiter(request: Request) -> None:
    client_ip = request.client.host if request.client else "unknown"
    check_rate_limit(
        scope="auth_login",
        identifier=client_ip,
        max_requests=5,
        window_seconds=10
    )

import os
import time
from collections import deque
from typing import Deque, Dict

from fastapi import HTTPException, Request


# ====== Config ======
MAX_TEXT_CHARS = int(os.getenv("MAX_TEXT_CHARS", "1200"))

# Rate limit: N requests per window seconds, per IP
RATE_LIMIT_MAX_REQUESTS = int(os.getenv("RATE_LIMIT_MAX_REQUESTS", "20"))
RATE_LIMIT_WINDOW_SECONDS = int(os.getenv("RATE_LIMIT_WINDOW_SECONDS", "60"))

# Optional: require a demo token for public usage
# If DEMO_TOKEN is set, requests must include header: X-Demo-Token: <token>
DEMO_TOKEN = os.getenv("DEMO_TOKEN", "").strip()


# In-memory rate limit store: ip -> deque[timestamps]
_rate_store: Dict[str, Deque[float]] = {}


def _get_client_ip(request: Request) -> str:
    """
    Cloud Run / proxies often pass X-Forwarded-For.
    We take the first IP if present, else fall back to request.client.host.
    """
    xff = request.headers.get("x-forwarded-for")
    if xff:
        return xff.split(",")[0].strip()
    client = request.client.host if request.client else "unknown"
    return client


def enforce_guardrails(request: Request, text: str) -> None:
    """
    Comprehensive guardrails for both API and web UI:
    - Optional demo token gate
    - Input length limits
    - Sliding window rate limiting per IP
    - Basic input validation
    """
    # 1) Optional demo token gate
    if DEMO_TOKEN:
        provided = request.headers.get("x-demo-token", "").strip()
        if provided != DEMO_TOKEN:
            raise HTTPException(status_code=401, detail="Missing/invalid demo token.")

    # 2) Input length limit
    if not isinstance(text, str) or not text.strip():
        raise HTTPException(status_code=400, detail="Text is required.")
    if len(text) > MAX_TEXT_CHARS:
        raise HTTPException(
            status_code=413,
            detail=f"Text too long. Max {MAX_TEXT_CHARS} characters.",
        )

    # 3) Sliding window rate limiting (in-memory, per IP)
    ip = _get_client_ip(request)
    now = time.time()

    q = _rate_store.get(ip)
    if q is None:
        q = deque()
        _rate_store[ip] = q

    # Drop timestamps outside the window
    cutoff = now - RATE_LIMIT_WINDOW_SECONDS
    while q and q[0] < cutoff:
        q.popleft()

    if len(q) >= RATE_LIMIT_MAX_REQUESTS:
        # Calculate wait time until oldest request expires
        wait_seconds = int(q[0] + RATE_LIMIT_WINDOW_SECONDS - now)
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded. Try again in {wait_seconds} seconds.",
        )

    q.append(now)

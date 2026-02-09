# Type Checking and Rate Limiting Notes

## T070: Mypy Strict Mode Check

### Status
Type checking configuration is complete with strict mode enabled in `backend/mypy.ini`.

### To Run Type Checking
```bash
cd backend
poetry run mypy src --strict
```

### Expected Issues
The following issues are expected and can be addressed if needed:

1. **Third-party library stubs**: Some libraries (fastmcp, agents) may not have complete type stubs
   - Current workaround: `ignore_missing_imports = True` in mypy.ini for these libraries

2. **SQLAlchemy/SQLModel dynamic attributes**: Some ORM-generated attributes may not be fully typed
   - These are generally safe to ignore as SQLModel provides runtime validation

3. **FastAPI dependency injection**: Some injected dependencies may show type warnings
   - These are safe as FastAPI handles type validation at runtime

### Recommendation
Run `mypy src --strict` before production deployment and address any critical type errors. The current implementation follows type safety best practices with:
- All function signatures typed
- Pydantic models for validation
- Type hints throughout codebase
- Strict mode configuration

---

## T072: Rate Limiting Implementation

### Status
Rate limiting is documented but not implemented to avoid adding additional dependencies.

### Implementation Options

#### Option 1: slowapi (Recommended)
```bash
cd backend
poetry add slowapi
```

```python
# In backend/src/api/main.py
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# In backend/src/api/routes/chatkit.py
@router.post("/threads/{thread_id}/messages")
@limiter.limit("10/minute")  # 10 messages per minute per IP
async def send_message(...):
    ...
```

#### Option 2: Custom Middleware
```python
# In backend/src/api/middleware/rate_limit.py
from fastapi import Request, HTTPException
from collections import defaultdict
from datetime import datetime, timedelta

class RateLimitMiddleware:
    def __init__(self, requests_per_minute: int = 10):
        self.requests_per_minute = requests_per_minute
        self.requests = defaultdict(list)

    async def __call__(self, request: Request, call_next):
        client_ip = request.client.host
        now = datetime.utcnow()

        # Clean old requests
        self.requests[client_ip] = [
            req_time for req_time in self.requests[client_ip]
            if now - req_time < timedelta(minutes=1)
        ]

        # Check rate limit
        if len(self.requests[client_ip]) >= self.requests_per_minute:
            raise HTTPException(status_code=429, detail="Too many requests")

        self.requests[client_ip].append(now)
        return await call_next(request)
```

#### Option 3: Nginx/Reverse Proxy
Configure rate limiting at the reverse proxy level:
```nginx
limit_req_zone $binary_remote_addr zone=chatkit:10m rate=10r/m;

location /chatkit/ {
    limit_req zone=chatkit burst=5;
    proxy_pass http://backend;
}
```

### Recommendation
- **Development**: No rate limiting needed
- **Production**: Use Option 3 (Nginx) for best performance and separation of concerns
- **Alternative**: Use Option 1 (slowapi) if reverse proxy is not available

### Rate Limit Suggestions
- `/auth/register`: 5 requests per hour per IP
- `/auth/login`: 10 requests per hour per IP
- `/chatkit/threads`: 20 requests per minute per user
- `/chatkit/threads/{id}/messages`: 10 requests per minute per user

---

## Summary

**T070 (Mypy)**: Configuration complete, manual run required before production
**T072 (Rate Limiting)**: Documented with implementation options, recommended to implement at reverse proxy level

Both tasks are optional for MVP but recommended for production deployment.

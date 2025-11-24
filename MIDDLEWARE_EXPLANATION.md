# Middleware Logic Explanation

## What `@app.middleware("http")` Means

```python
@app.middleware("http")
async def require_internal_api_key(request: Request, call_next):
```

**This is NOT checking if the path contains "http"!**

`@app.middleware("http")` is a **FastAPI decorator** that means:

- "Run this middleware function for **ALL HTTP requests** to this service"
- It's the way FastAPI registers HTTP request middleware
- The `"http"` is just the middleware type name, not a path check

## Actual Middleware Logic Flow

Here's what the middleware actually does:

```python
@app.middleware("http")  # ← Runs for ALL HTTP requests
async def require_internal_api_key(request: Request, call_next):

    # STEP 1: Check if path is for agent card discovery
    if request.url.path.startswith("/.well-known"):
        return await call_next(request)  # ← Skip auth, allow through

    # STEP 2: Check if API key authentication is enabled
    if A2A_API_KEY:  # ← Only if A2A_API_KEY is set in .env
        # STEP 3: Get the API key from the HTTP request header
        provided_key = request.headers.get("x-internal-api-key")

        # STEP 4: Compare with expected key
        if provided_key != A2A_API_KEY:
            # STEP 5: Log warning if key is missing/wrong
            print(f"[AUTH WARNING] Missing/invalid API key...")

    # STEP 6: Continue processing the request
    return await call_next(request)
```

## When the API Key is Checked

The middleware checks for the API key in the header on **ALL requests EXCEPT**:

1. ✅ **Agent card discovery** (`/.well-known/*` paths) - Always allowed (no auth needed)
2. ✅ **All other paths** (`/tasks`, `/`, etc.) - **API key is checked**

## Example Request Flow

### Request 1: Agent Card Discovery

```
Request: GET http://localhost:8002/.well-known/agent-card.json
         Headers: (none needed)

Middleware:
  → Path starts with "/.well-known"? YES
  → Skip auth check ✅
  → Allow request through
```

### Request 2: Task Execution (Agent Call)

```
Request: POST http://localhost:8002/tasks
         Headers: x-internal-api-key: your-secret-key

Middleware:
  → Path starts with "/.well-known"? NO
  → A2A_API_KEY is set? YES
  → Get header "x-internal-api-key": "your-secret-key"
  → Compare with A2A_API_KEY: Match? YES
  → No warning ✅
  → Allow request through
```

### Request 3: Task Execution (No Key)

```
Request: POST http://localhost:8002/tasks
         Headers: (no x-internal-api-key)

Middleware:
  → Path starts with "/.well-known"? NO
  → A2A_API_KEY is set? YES
  → Get header "x-internal-api-key": None
  → Compare with A2A_API_KEY: Match? NO
  → Print [AUTH WARNING] ⚠️
  → Still allow request through (soft mode)
```

## Summary

- **`@app.middleware("http")`** = "Run for all HTTP requests" (not checking for "http" in path)
- **API key is checked** on all paths EXCEPT `/.well-known/*`
- **The check happens** at line 50: `request.headers.get("x-internal-api-key")`
- **If key is missing/wrong**, you'll see `[AUTH WARNING]` in service logs

The middleware intercepts **every HTTP request** and checks the `x-internal-api-key` header (except for agent card discovery).

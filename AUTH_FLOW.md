# Authentication Flow: Where the API Key is Checked

## Current Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│  Customer Support Agent (client/customer_support_client.py)    │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Creates RemoteA2aAgent proxies                         │  │
│  │  ❌ Currently does NOT send API key header                │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                            │
                            │ HTTP POST to /tasks
                            │ (without x-internal-api-key header)
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  Service (e.g., services/inventory_service.py)                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Middleware: require_internal_api_key()                   │  │
│  │  Line 38-52: Checks for "x-internal-api-key" header      │  │
│  │  ✅ THIS IS WHERE THE KEY IS CHECKED                       │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## Where the API Key is Checked (Server Side)

### Location: `services/*_service.py` - Lines 38-52

```python
# Add API key authentication middleware
@app.middleware("http")
async def require_internal_api_key(request: Request, call_next):
    # Allow agent card discovery (needed for RemoteA2aAgent)
    if request.url.path.startswith("/.well-known"):
        return await call_next(request)

    if A2A_API_KEY:  # ← Line 44: Checks if API key is configured
        provided_key = request.headers.get("x-internal-api-key")  # ← Line 45: Gets header
        if provided_key != A2A_API_KEY:  # ← Line 46: Compares with expected key
            # Soft mode (won't break your current setup):
            print(f"[AUTH WARNING] Missing/invalid API key for path {request.url.path}")  # ← Line 48: LOGS WARNING
            # When ready to enforce security:
            # raise HTTPException(status_code=401, detail="Unauthorized")

    return await call_next(request)
```

**Key Points:**

- **Line 45**: `request.headers.get("x-internal-api-key")` - This is where it reads the API key from the HTTP header
- **Line 46**: `if provided_key != A2A_API_KEY` - This is where it validates the key
- **Line 48**: `print(f"[AUTH WARNING]...")` - This is where you'll see if the key is missing/wrong

## Current Problem: Agents Don't Send the Key

### Location: `client/customer_support_client.py` - Lines 40-64

```python
remote_product_catalog_agent = RemoteA2aAgent(
    name="product_catalog_agent",
    description="Remote product catalog agent...",
    agent_card=f"http://localhost:8001{AGENT_CARD_WELL_KNOWN_PATH}",
    # ❌ No API key header is being sent here
)
```

**The Issue:** `RemoteA2aAgent` doesn't have a built-in parameter to send custom headers like `x-internal-api-key`.

## How to Verify if Agents Are Using the Key

### Method 1: Check Service Logs (Current Setup)

When agents communicate, watch the service terminal windows:

**If agents are NOT sending the key:**

```
[AUTH WARNING] Missing/invalid API key for path /tasks
```

**If agents ARE sending the correct key:**

```
(No warning message - request proceeds silently)
```

### Method 2: Add Logging to See Incoming Headers

You can temporarily add logging to see what headers are being received:

```python
@app.middleware("http")
async def require_internal_api_key(request: Request, call_next):
    if request.url.path.startswith("/.well-known"):
        return await call_next(request)

    if A2A_API_KEY:
        # DEBUG: Log all headers (remove in production)
        print(f"[DEBUG] Request to {request.url.path}")
        print(f"[DEBUG] Headers: {dict(request.headers)}")
        print(f"[DEBUG] API Key in header: {request.headers.get('x-internal-api-key', 'NOT FOUND')}")

        provided_key = request.headers.get("x-internal-api-key")
        if provided_key != A2A_API_KEY:
            print(f"[AUTH WARNING] Missing/invalid API key for path {request.url.path}")

    return await call_next(request)
```

## Solution: Make Agents Send the API Key

Since `RemoteA2aAgent` may not support custom headers directly, you have a few options:

### Option 1: Check if RemoteA2aAgent Supports Headers

Check the Google ADK documentation or try:

```python
remote_agent = RemoteA2aAgent(
    name="product_catalog_agent",
    agent_card=f"http://localhost:8001{AGENT_CARD_WELL_KNOWN_PATH}",
    # Check if there's a headers or http_client_config parameter
)
```

### Option 2: Use Environment-Based Authentication

Instead of header-based auth, you could:

- Use IP whitelisting
- Use mTLS certificates
- Use a different authentication method supported by the A2A protocol

### Option 3: Create a Proxy/Wrapper

Create a wrapper that adds headers before calling RemoteA2aAgent (if the library supports it).

## Testing the Current Setup

1. **Run your services** with `A2A_API_KEY` set in `.env`
2. **Run the customer support client** to trigger agent communication
3. **Watch the service terminal windows** - you should see `[AUTH WARNING]` messages
4. **This confirms:**
   - ✅ Middleware is working (checking for key)
   - ❌ Agents are NOT sending the key (hence the warnings)

## Summary

- **Where key is checked:** `services/*_service.py` lines 44-50 (middleware)
- **How to verify:** Check service logs for `[AUTH WARNING]` messages
- **Current status:** Agents don't send the key (you'll see warnings)
- **Next step:** Find a way to make `RemoteA2aAgent` send the `x-internal-api-key` header

# Testing A2A API Key Authentication

This guide explains how to test the API key authentication for your AI agents.

## Quick Start

1. **Set the API key in your `.env` file:**

   ```bash
   A2A_API_KEY=your-secret-key-123
   ```

2. **Start all services** (in separate terminals):

   ```bash
   python -m services.product_catalog_service
   python -m services.inventory_service
   python -m services.shipping_service
   python -m services.payment_service
   ```

3. **Run the test script:**
   ```bash
   python test_auth.py
   ```

## What the Test Does

The `test_auth.py` script tests:

1. **Agent Card Discovery** - Verifies that `/.well-known/agent-card.json` endpoints work without authentication (required for RemoteA2aAgent to discover agents)

2. **Task Endpoints Without API Key** - Tests that requests to `/tasks` without the API key trigger warnings (in soft mode) or are rejected (in hard mode)

3. **Task Endpoints With Wrong API Key** - Tests that requests with incorrect API keys are detected

4. **Task Endpoints With Correct API Key** - Tests that requests with the correct API key work without warnings

## Understanding the Results

### Soft Mode (Current Default)

When `A2A_API_KEY` is set but the middleware is in soft mode:

- ✅ Requests work regardless of API key
- ⚠️ Warnings are logged to service console: `[AUTH WARNING] Missing/invalid API key for path /tasks`
- ✅ Requests with correct API key show no warnings

**Watch the service terminal windows** to see the authentication warnings!

### Hard Mode (Enforcement)

To enable hard enforcement, uncomment this line in each service file:

```python
raise HTTPException(status_code=401, detail="Unauthorized")
```

In hard mode:

- ✅ Requests with correct API key work
- ❌ Requests without/wrong API key return 401 Unauthorized

## Testing with RemoteA2aAgent

Currently, `RemoteA2aAgent` may not support custom headers directly. If you need to test the full agent-to-agent flow with authentication:

1. **Keep authentication in soft mode** (current setup) - this allows testing while logging warnings
2. **Monitor service logs** to see authentication warnings when agents communicate
3. **For production**, you may need to:
   - Use a proxy/wrapper that adds headers
   - Wait for RemoteA2aAgent to support custom headers
   - Or use a different authentication method (e.g., IP whitelisting, mTLS)

## Manual Testing with curl

You can also test manually using `curl`:

```bash
# Test without API key (should show warning in service logs)
curl -X POST http://localhost:8001/tasks \
  -H "Content-Type: application/json" \
  -d '{"test": "data"}'

# Test with wrong API key (should show warning in service logs)
curl -X POST http://localhost:8001/tasks \
  -H "Content-Type: application/json" \
  -H "x-internal-api-key: wrong-key" \
  -d '{"test": "data"}'

# Test with correct API key (should work, no warnings)
curl -X POST http://localhost:8001/tasks \
  -H "Content-Type: application/json" \
  -H "x-internal-api-key: your-secret-key-123" \
  -d '{"test": "data"}'

# Test agent card (should always work)
curl http://localhost:8001/.well-known/agent-card.json
```

## Troubleshooting

- **No warnings appearing?** Make sure `A2A_API_KEY` is set in your `.env` file
- **Services not starting?** Check that `GOOGLE_API_KEY` is set
- **Connection errors?** Make sure all services are running before testing

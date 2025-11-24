"""
Shipping A2A Service

Exposes the Shipping Agent via A2A protocol on port 8003.
This service can be run with: python -m services.shipping_service
Or with uvicorn: uvicorn services.shipping_service:app --host localhost --port 8003

Extracted from notebook Cell 34 (Shipping Agent section).
"""

import os
from dotenv import load_dotenv
from fastapi import Request, HTTPException
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from agents.shipping_agent import create_shipping_agent

# Load environment variables from .env file (if it exists)
load_dotenv()

# Ensure GOOGLE_API_KEY is set (required for Gemini API)
if not os.environ.get("GOOGLE_API_KEY"):
    raise ValueError(
        "GOOGLE_API_KEY environment variable must be set. "
        "Either create a .env file with GOOGLE_API_KEY=your-key-here "
        "or set it with: export GOOGLE_API_KEY='your-key-here'"
    )

# Load A2A API key for authentication (optional - set A2A_API_KEY in .env to enable)
A2A_API_KEY = os.environ.get("A2A_API_KEY")

# Create the agent
shipping_agent = create_shipping_agent()

# Expose the agent via A2A protocol
app = to_a2a(shipping_agent, port=8003)

# Add API key authentication middleware
@app.middleware("http")
async def require_internal_api_key(request: Request, call_next):
    # Allow agent card discovery (needed for RemoteA2aAgent)
    if request.url.path.startswith("/.well-known"):
        return await call_next(request)

    if A2A_API_KEY:
        provided_key = request.headers.get("x-internal-api-key")
        if provided_key != A2A_API_KEY:
            # Soft mode (won't break your current setup):
            print(f"[AUTH WARNING] Missing/invalid API key for path {request.url.path}")
            # When ready to enforce security:
            # raise HTTPException(status_code=401, detail="Unauthorized")

    return await call_next(request)

if __name__ == "__main__":
    import uvicorn

    print("🚀 Starting Shipping Agent server...")
    print("   Server URL: http://localhost:8003")
    print("   Agent card: http://localhost:8003/.well-known/agent-card.json")
    uvicorn.run(app, host="localhost", port=8003)



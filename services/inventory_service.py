"""
Inventory A2A Service

Exposes the Inventory Agent via A2A protocol on port 8002.
This service can be run with: python -m services.inventory_service
Or with uvicorn: uvicorn services.inventory_service:app --host localhost --port 8002

Extracted from notebook Cell 34 (Inventory Agent section).
"""

import os
from dotenv import load_dotenv
from fastapi import Request, HTTPException
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from agents.inventory_agent import create_inventory_agent

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
inventory_agent = create_inventory_agent()

# Expose the agent via A2A protocol
app = to_a2a(inventory_agent, port=8002)

# Add API key authentication middleware
@app.middleware("http")
async def require_internal_api_key(request: Request, call_next):
    # Allow agent card discovery (needed for RemoteA2aAgent)
    if request.url.path.startswith("/.well-known"):
        return await call_next(request)

    if A2A_API_KEY:
        # DEBUG: Log authentication details (uncomment to see what headers agents are sending)
        # print(f"[AUTH DEBUG] Request to {request.url.path}")
        # print(f"[AUTH DEBUG] API Key header present: {request.headers.get('x-internal-api-key') is not None}")
        # print(f"[AUTH DEBUG] All headers: {dict(request.headers)}")
        
        provided_key = request.headers.get("x-internal-api-key")
        if provided_key != A2A_API_KEY:
            # Soft mode (won't break your current setup):
            print(f"[AUTH WARNING] Missing/invalid API key for path {request.url.path}")
            print(f"              Expected: {A2A_API_KEY[:20]}... (truncated)")
            print(f"              Received: {provided_key if provided_key else 'NONE'}")
            # When ready to enforce security:
            # raise HTTPException(status_code=401, detail="Unauthorized")
        else:
            # Log successful authentication (optional - comment out in production)
            # print(f"[AUTH SUCCESS] Valid API key provided for {request.url.path}")
            pass

    return await call_next(request)

if __name__ == "__main__":
    import uvicorn

    print("🚀 Starting Inventory Agent server...")
    print("   Server URL: http://localhost:8002")
    print("   Agent card: http://localhost:8002/.well-known/agent-card.json")
    uvicorn.run(app, host="localhost", port=8002)



"""
Customer Support Client

Test harness for the Customer Support Agent that communicates with remote agents via A2A.

This script:
1. Creates RemoteA2aAgent proxies pointing to each A2A service
2. Creates the Customer Support Agent with these remote agents as sub-agents
3. Provides a test function to send queries and display responses

Extracted from notebook Cells 21, 32, 33, 36, and 37.
"""

import asyncio
import uuid
# Import compatibility shim BEFORE any aiohttp-dependent imports
import aiohttp_compat  # noqa: F401
from dotenv import load_dotenv
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent, AGENT_CARD_WELL_KNOWN_PATH
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from agents.customer_support_agent import create_customer_support_agent

# Load environment variables from .env file (if it exists)
load_dotenv()


def create_remote_agents():
    """Create RemoteA2aAgent proxies for each A2A service.
    
    These proxies act as client-side interfaces to the remote agents.
    They read the agent card from each service and translate sub-agent calls
    into A2A protocol requests (HTTP POST to /tasks).
    
    Returns:
        Tuple of (remote_product_catalog_agent, remote_inventory_agent, remote_shipping_agent, remote_payment_agent)
    """
    # Product Catalog Agent
    remote_product_catalog_agent = RemoteA2aAgent(
        name="product_catalog_agent",
        description="Remote product catalog agent from external vendor that provides product information.",
        agent_card=f"https://web-production-b8d5.up.railway.app{AGENT_CARD_WELL_KNOWN_PATH}",
    )

    # Inventory Agent
    remote_inventory_agent = RemoteA2aAgent(
        name="inventory_agent",
        description="Remote inventory agent from external vendor that provides stock levels and restocking schedules.",
        agent_card=f"https://web-production-b8d5.up.railway.app{AGENT_CARD_WELL_KNOWN_PATH}",
    )

    # Shipping Agent
    remote_shipping_agent = RemoteA2aAgent(
        name="shipping_agent",
        description="Remote shipping agent from external vendor that provides delivery estimates and package tracking information.",
        agent_card=f"https://web-production-b8d5.up.railway.app{AGENT_CARD_WELL_KNOWN_PATH}",
    )

    remote_payment_agent = RemoteA2aAgent(
        name="payment_agent",
        description="Remote payment microservice that handles Stripe payments.",
        agent_card=f"https://web-production-b8d5.up.railway.app{AGENT_CARD_WELL_KNOWN_PATH}",
    )

    return remote_product_catalog_agent, remote_inventory_agent, remote_shipping_agent, remote_payment_agent


async def test_a2a_communication(customer_support_agent, user_query: str):
    """Test the A2A communication between Customer Support Agent and remote agents.

    This function:
    1. Creates a new session for this conversation
    2. Sends the query to the Customer Support Agent
    3. Support Agent communicates with remote agents via A2A
    4. Displays the response

    Args:
        customer_support_agent: The Customer Support Agent instance
        user_query: The question to ask the Customer Support Agent
    """
    # Setup session management (required by ADK)
    session_service = InMemorySessionService()

    # Session identifiers
    app_name = "support_app"
    user_id = "demo_user"
    # Use unique session ID for each test to avoid conflicts
    session_id = f"demo_session_{uuid.uuid4().hex[:8]}"

    # CRITICAL: Create session BEFORE running agent
    # This pattern matches the deployment notebook exactly
    session = await session_service.create_session(
        app_name=app_name, user_id=user_id, session_id=session_id
    )

    # Create runner for the Customer Support Agent
    # The runner manages the agent execution and session state
    runner = Runner(
        agent=customer_support_agent, app_name=app_name, session_service=session_service
    )

    # Create the user message
    test_content = types.Content(parts=[types.Part(text=user_query)])

    # Display query
    print(f"\n👤 Customer: {user_query}")
    print(f"\n🎧 Support Agent response:")
    print("-" * 60)

    # Run the agent asynchronously (handles streaming responses and A2A communication)
    async for event in runner.run_async(
        user_id=user_id, session_id=session_id, new_message=test_content
    ):
        # Print final response only (skip intermediate events)
        if event.is_final_response() and event.content:
            for part in event.content.parts:
                if hasattr(part, "text"):
                    print(part.text)

    print("-" * 60)


async def main():
    """Main function to run the test harness."""
    print("🧪 Testing A2A Communication...\n")
    print("⚠️  Make sure all four A2A services are running on Railway:")
    print("   - Product Catalog Agent: https://web-production-b8d5.up.railway.app")
    print("   - Inventory Agent: https://web-production-b8d5.up.railway.app")
    print("   - Shipping Agent: https://web-production-b8d5.up.railway.app")
    print("   - Payment Agent: https://web-production-b8d5.up.railway.app\n")

    # Create remote agent proxies
    (
        remote_product_catalog_agent,
        remote_inventory_agent,
        remote_shipping_agent,
        remote_payment_agent,
    ) = create_remote_agents()

    # Create the Customer Support Agent with remote sub-agents
    customer_support_agent = create_customer_support_agent(
        remote_product_catalog_agent,
        remote_inventory_agent,
        remote_shipping_agent,
        remote_payment_agent,
    )

    print("✅ Customer Support Agent created with 4 remote sub-agents\n")

    # Run test queries
    test_queries = [
        "Can you tell me about the iPhone 15 Pro? Is it in stock?",
        "Is the MacBook Pro 14 in stock?",
        "How long will it take to ship an iPhone 15 Pro to San Francisco?",
        "Where is package with tracking number 1Z999?",
        "Can you charge me $9.99 in USD for my new iPhone? My email is test@example.com",
    ]

    for query in test_queries:
        await test_a2a_communication(customer_support_agent, query)
        print()  # Blank line between queries


if __name__ == "__main__":
    asyncio.run(main())



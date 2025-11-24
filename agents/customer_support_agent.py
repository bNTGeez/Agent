"""
Customer Support Agent

Coordinates multiple remote agents (Product Catalog, Inventory, Shipping) to help customers.
This agent consumes remote agents via A2A protocol using RemoteA2aAgent proxies.

Extracted from notebook Cell 36.
"""

from google.adk.agents import LlmAgent
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent, AGENT_CARD_WELL_KNOWN_PATH
from google.adk.models.google_llm import Gemini
from config import retry_config


def create_customer_support_agent(
    remote_product_catalog_agent: RemoteA2aAgent,
    remote_inventory_agent: RemoteA2aAgent,
    remote_shipping_agent: RemoteA2aAgent,
    remote_payment_agent: RemoteA2aAgent,
) -> LlmAgent:
    """Create the Customer Support Agent.
    
    This agent uses four remote agents as sub-agents:
    - product_catalog_agent: For product details (price, specs, description)
    - inventory_agent: For stock/availability information
    - shipping_agent: For shipping speed, delivery estimates, and tracking
    - payment_agent: For billing, charges, refunds, and payment status
    
    The agent routes customer queries to the appropriate sub-agent based on the question type.
    
    Args:
        remote_product_catalog_agent: RemoteA2aAgent proxy for product catalog service
        remote_inventory_agent: RemoteA2aAgent proxy for inventory service
        remote_shipping_agent: RemoteA2aAgent proxy for shipping service
        remote_payment_agent: RemoteA2aAgent proxy for payment service
    
    Returns:
        LlmAgent configured for customer support with four sub-agents
    """
    agent = LlmAgent(
        model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
        name="customer_support_agent",
        description="A customer support assistant that helps customers with product inquiries and information.",
        instruction="""
        You are a friendly and professional customer support agent.

        When customers ask about:
        - Product details (price, specs, description): ALWAYS use product_catalog_agent.
        - Stock / availability: ALWAYS use inventory_agent.
        - Shipping speed, delivery estimates, or tracking: ALWAYS use shipping_agent.
        Never answer shipping questions from your own knowledge; you must call shipping_agent.
        - For billing, charges, refunds, or payment status questions, ALWAYS delegate to payment_agent.

        Examples:
        - "Charge me $9.99 for an iPhone 15 Pro" -> payment_agent (create_payment_intent)
        - "What is the status of payment pi_123?" -> payment_agent (get_payment_status)

        Combine results from multiple sub-agents when the question asks about more than one of these.
        Be clear, helpful, and professional.
        """,
        sub_agents=[
            remote_product_catalog_agent,
            remote_inventory_agent,
            remote_shipping_agent,
            remote_payment_agent,
        ],
    )
    return agent



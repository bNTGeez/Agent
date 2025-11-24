"""
Inventory Agent

Reports stock levels and restocking schedules for products.
This agent is exposed via A2A so other agents can query inventory status.

Extracted from notebook Cell 30.
"""

import logging
import psycopg2
from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from config import retry_config
from db.inventory_queries import query_inventory

logger = logging.getLogger(__name__)


def get_inventory_info(product_name: str) -> str:
    """Get inventory information for a given product.

    Args:
        product_name: Name of the product

    Returns:
        Inventory status as a string (stock level and restock ETA if applicable)
    """
    try:
        record = query_inventory(product_name)

        if not record:
            return f"No inventory information found for '{product_name}'."

        return f"{product_name} is {record['status']} with {record['quantity']} units available."
    except psycopg2.Error as e:
        logger.error("DB Error in get_inventory_info: %s", e)
        return "Database error occurred. Please try again later."
    except Exception as e:
        logger.error("Unexpected error in get_inventory_info: %s", e)
        return "Unexpected error occurred."


def create_inventory_agent() -> LlmAgent:
    """Create the Inventory Agent.
    
    This agent specializes in providing inventory status and restocking information.
    The tool get_inventory_info is registered so the agent can check stock levels.
    
    Returns:
        LlmAgent configured for inventory queries
    """
    agent = LlmAgent(
        model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
        name="inventory_agent",
        description="External vendor's inventory agent that reports stock levels and restocking schedules.",
        instruction="""
        You are an inventory specialist from an external vendor.
        When asked about product availability, use the get_inventory_info tool to check stock levels and restock dates.
        Provide clear, accurate information about inventory status.
        If asked about multiple items, handle each one separately.
        Be concise, direct, and professional.
        """,
        tools=[get_inventory_info],
    )
    return agent



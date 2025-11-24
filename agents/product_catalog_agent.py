"""
Product Catalog Agent

Provides product information from an external vendor's catalog.
This agent is exposed via A2A so other agents (like customer support) can use it.

Extracted from notebook Cell 13.
"""

import logging
import psycopg2
from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from config import retry_config
from db.product_queries import query_product_by_name

logger = logging.getLogger(__name__)


def get_product_info(product_name: str) -> str:
    """Get product information for a given product.

    Args:
        product_name: Name of the product (e.g., "iPhone 15 Pro", "MacBook Pro")

    Returns:
        Product information as a string
    """
    try:
        record = query_product_by_name(product_name)

        if not record:
            return f"No product found for '{product_name}'."

        dollars = record['price_cents'] / 100

        return (
            f"Product: {record['name']}\n"
            f"Description: {record['description']}\n"
            f"Price: ${dollars:.2f}"
        )
    except psycopg2.Error as e:
        logger.error("DB Error in get_product_info: %s", e)
        return "Database error occurred. Please try again later."
    except Exception as e:
        logger.error("Unexpected error in get_product_info: %s", e)
        return "Unexpected error occurred."


def create_product_catalog_agent() -> LlmAgent:
    """Create the Product Catalog Agent.
    
    This agent specializes in providing product information from the vendor's catalog.
    The tool get_product_info is registered so the agent can look up products.
    
    Returns:
        LlmAgent configured for product catalog queries
    """
    agent = LlmAgent(
        model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
        name="product_catalog_agent",
        description="External vendor's product catalog agent that provides product information and availability.",
        instruction="""
        You are a product catalog specialist from an external vendor.
        When asked about products, use the get_product_info tool to fetch data from the catalog.
        Provide clear, accurate product information including price, availability, and specs.
        If asked about multiple products, look up each one.
        Be professional and helpful.
        """,
        tools=[get_product_info],  # Register the product lookup tool
    )
    return agent



"""
Shipping Agent

Provides delivery estimates and package tracking information.
This agent is exposed via A2A so other agents can query shipping details.

Extracted from notebook Cell 31.
"""

import logging
import psycopg2
from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from config import retry_config
from db.shipping_queries import query_shipping_estimate, query_tracking

logger = logging.getLogger(__name__)


def get_shipping_estimate(product_name: str, destination: str) -> str:
    """Use Postgres instead of dicts."""
    try:
        record = query_shipping_estimate(product_name)

        if not record:
            return f"No shipping estimate found for '{product_name}'."

        return (
            f"Standard: {record['standard_days']} ({record['standard_cost']}), "
            f"Express: {record['express_days']} ({record['express_cost']}). "
            f"Destination: {destination}."
        )
    except psycopg2.Error as e:
        logger.error("DB Error in get_shipping_estimate: %s", e)
        return "Database error occurred. Please try again later."
    except Exception as e:
        logger.error("Unexpected error in get_shipping_estimate: %s", e)
        return "Unexpected error occurred."


def get_tracking_info(tracking_number: str) -> str:
    """Use Postgres instead of dicts."""
    try:
        t = query_tracking(tracking_number)

        if not t:
            return f"No tracking data found for tracking number '{tracking_number}'."

        return (
            f"Status: {t['status']}. "
            f"Last seen in {t['last_location']}. "
            f"Estimated delivery: {t['eta']}."
        )
    except psycopg2.Error as e:
        logger.error("DB Error in get_tracking_info: %s", e)
        return "Database error occurred. Please try again later."
    except Exception as e:
        logger.error("Unexpected error in get_tracking_info: %s", e)
        return "Unexpected error occurred."


def create_shipping_agent() -> LlmAgent:
    """Create the Shipping Agent.
    
    This agent specializes in providing shipping estimates and tracking information.
    Two tools are registered: get_shipping_estimate and get_tracking_info.
    
    Returns:
        LlmAgent configured for shipping queries
    """
    agent = LlmAgent(
        model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
        name="shipping_agent",
        description="External vendor's shipping agent that provides delivery estimates and package tracking information.",
        instruction="""
        You are a shipping specialist from an external vendor.
        When asked about shipping, use the get_shipping_estimate and get_tracking_info tools to provide delivery estimates and tracking information.
        Return clear, accurate details about shipping timelines, costs, carriers, and tracking status.
        If asked about multiple shipments, handle each one separately.
        Be concise, direct, and professional.
        """,
        tools=[get_shipping_estimate, get_tracking_info],
    )
    return agent



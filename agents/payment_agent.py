import os
import logging
import psycopg2
import stripe
import stripe.error
from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from tenacity import retry, stop_after_attempt, wait_exponential

from config import retry_config
from db.payment_queries import insert_payment, get_payment_by_intent

load_dotenv()

logger = logging.getLogger(__name__)

STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
stripe.api_key = STRIPE_SECRET_KEY


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=0.2, min=0.2, max=2))
def create_payment_intent(amount: float, currency: str, customer_email: str) -> str:
    """
    Create a Stripe PaymentIntent in test mode.

    amount: in major units (e.g. 99.99 for $99.99)
    currency: 'usd', 'eur', etc.
    customer_email: email string (can be used to attach to customer later)
    """
    if not STRIPE_SECRET_KEY:
        return "ERROR: Stripe secret key is not configured."

    try:
        amount_cents = int(round(amount * 100))

        intent = stripe.PaymentIntent.create(
            amount=amount_cents,
            currency=currency,
            receipt_email=customer_email,
            automatic_payment_methods={"enabled": True},
        )

        # Log to our own DB
        try:
            insert_payment(
                stripe_payment_intent_id=intent.id,
                amount_cents=amount_cents,
                currency=currency,
                customer_email=customer_email,
                status=intent.status,
            )
        except psycopg2.Error as e:
            logger.error("DB Error in create_payment_intent: %s", e)
            # Continue even if DB write fails
        except Exception as e:
            logger.error("Unexpected DB error in create_payment_intent: %s", e)
            # Continue even if DB write fails

        return (
            f"Created payment intent.\n"
            f"ID: {intent.id}\n"
            f"Status: {intent.status}\n"
            f"Amount: {amount:.2f} {currency.upper()}\n"
            f"Client secret (for frontend): {intent.client_secret}"
        )

    except stripe.error.APIConnectionError as e:
        logger.error("Stripe connection error in create_payment_intent: %s", e)
        return "Payment service is temporarily unavailable."
    except stripe.error.StripeError as e:
        logger.error("Stripe error in create_payment_intent: %s", e)
        return "Payment service error occurred. Please try again later."
    except Exception as e:
        logger.error("Unexpected error in create_payment_intent: %s", e)
        return (
            "Sorry, I couldn't process your payment request right now. "
            "The payment system is temporarily unavailable. Please try again later."
        )


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=0.2, min=0.2, max=2))
def get_payment_status(payment_intent_id: str) -> str:
    """
    Look up current status of a Stripe PaymentIntent.
    """
    if not STRIPE_SECRET_KEY:
        return "ERROR: Stripe secret key is not configured."

    try:
        intent = stripe.PaymentIntent.retrieve(payment_intent_id)
    except stripe.error.APIConnectionError as e:
        logger.error("Stripe connection error in get_payment_status: %s", e)
        return "Payment service is temporarily unavailable."
    except stripe.error.StripeError as e:
        logger.error("Stripe error in get_payment_status: %s", e)
        return "Payment service error occurred. Please try again later."
    except Exception as e:
        logger.error("Unexpected error in get_payment_status: %s", e)
        return (
            "Sorry, I couldn't retrieve the payment status right now. "
            "The payment system is temporarily unavailable. Please try again later."
        )

    # Optionally, sync to our DB
    try:
        insert_payment(
            stripe_payment_intent_id=intent.id,
            amount_cents=int(intent.amount),
            currency=intent.currency,
            customer_email=intent.get("receipt_email"),
            status=intent.status,
        )
    except psycopg2.Error as e:
        logger.error("DB Error in get_payment_status: %s", e)
        # If DB write fails, don't kill the response
    except Exception as e:
        logger.error("Unexpected DB error in get_payment_status: %s", e)
        # If DB write fails, don't kill the response

    amount = intent.amount / 100.0 if intent.amount is not None else None

    return (
        f"Payment intent {intent.id} has status '{intent.status}'. "
        f"Amount: {amount:.2f} {intent.currency.upper()}."
    )


def create_payment_agent() -> LlmAgent:
    """
    Payment Agent that knows how to create and check Stripe payments.
    """
    return LlmAgent(
        model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
        name="payment_agent",
        description="Handles payment creation and payment status queries via Stripe.",
        instruction="""
        You are a billing and payments specialist.
        - Use create_payment_intent to create payments when a user wants to purchase something.
        - Use get_payment_status to check the current state of an existing payment.
        Never invent payment ids or statuses. Always rely on tools.
        """,
        tools=[create_payment_intent, get_payment_status],
    )

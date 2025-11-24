import logging
import psycopg2
from db.connection import get_db
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=0.2, min=0.2, max=2))
def insert_payment(stripe_payment_intent_id: str, amount_cents: int, currency: str,
                   customer_email: str | None, status: str):
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            """
            insert into payments (stripe_payment_intent_id, amount_cents, currency, customer_email, status)
            values (%s, %s, %s, %s, %s)
            on conflict (stripe_payment_intent_id) do update
            set status = excluded.status;
            """,
            (stripe_payment_intent_id, amount_cents, currency, customer_email, status)
        )
        conn.commit()
        cur.close()
        conn.close()
    except psycopg2.Error as e:
        logger.error("DB Error in insert_payment: %s", e)
        raise
    except Exception as e:
        logger.error("Unexpected error in insert_payment: %s", e)
        raise


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=0.2, min=0.2, max=2))
def get_payment_by_intent(stripe_payment_intent_id: str):
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            """
            select stripe_payment_intent_id, amount_cents, currency, customer_email, status, created_at
            from payments
            where stripe_payment_intent_id = %s
            limit 1;
            """,
            (stripe_payment_intent_id,)
        )
        row = cur.fetchone()
        cur.close()
        conn.close()
        return row
    except psycopg2.Error as e:
        logger.error("DB Error in get_payment_by_intent: %s", e)
        raise
    except Exception as e:
        logger.error("Unexpected error in get_payment_by_intent: %s", e)
        raise

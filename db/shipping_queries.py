import logging
import psycopg2
from db.connection import get_db
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=0.2, min=0.2, max=2))
def query_shipping_estimate(product_name: str):
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            """
            SELECT standard_days, standard_cost, express_days, express_cost
            FROM shipping_estimates
            WHERE LOWER(product_name) = LOWER(%s)
            LIMIT 1;
            """,
            (product_name,)
        )
        row = cur.fetchone()
        cur.close()
        conn.close()
        return row
    except psycopg2.Error as e:
        logger.error("DB Error in query_shipping_estimate: %s", e)
        raise
    except Exception as e:
        logger.error("Unexpected error in query_shipping_estimate: %s", e)
        raise


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=0.2, min=0.2, max=2))
def query_tracking(tracking_number: str):
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            """
            SELECT status, last_location, eta
            FROM tracking_info
            WHERE tracking_number = %s
            LIMIT 1;
            """,
            (tracking_number,)
        )
        row = cur.fetchone()
        cur.close()
        conn.close()
        return row
    except psycopg2.Error as e:
        logger.error("DB Error in query_tracking: %s", e)
        raise
    except Exception as e:
        logger.error("Unexpected error in query_tracking: %s", e)
        raise

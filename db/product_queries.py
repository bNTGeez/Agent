import logging
import psycopg2
from db.connection import get_db
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=0.2, min=0.2, max=2))
def query_product_by_name(name: str):
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            """
            SELECT id, name, description, price_cents
            FROM products
            WHERE LOWER(name) = LOWER(%s)
            LIMIT 1;
            """,
            (name,)
        )
        row = cur.fetchone()
        cur.close()
        conn.close()
        return row
    except psycopg2.Error as e:
        logger.error("DB Error in query_product_by_name: %s", e)
        raise
    except Exception as e:
        logger.error("Unexpected error in query_product_by_name: %s", e)
        raise

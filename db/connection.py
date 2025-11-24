# db/connection.py
import os
import logging
import psycopg2
from dotenv import load_dotenv
from psycopg2.extras import RealDictCursor
from tenacity import retry, stop_after_attempt, wait_exponential

load_dotenv()

logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL")

def get_db():
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=0.2, min=0.2, max=2))
    def _connect():
        if not DATABASE_URL:
            raise RuntimeError("DATABASE_URL is not set")
        return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
    
    try:
        return _connect()
    except psycopg2.Error as e:
        logger.error("Database connection error: %s", e)
        raise
    except Exception as e:
        logger.error("Unexpected error connecting to database: %s", e)
        raise

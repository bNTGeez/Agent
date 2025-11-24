"""
Configuration shared across all agents and services.

This module contains retry configuration and other shared settings.
Extracted from notebook Cell 11.
"""

from google.genai import types

# Retry configuration for LLM API calls
# Handles transient errors like rate limits (429) and service unavailability (500, 503, 504)
retry_config = types.HttpRetryOptions(
    attempts=5,  # Maximum retry attempts
    exp_base=7,  # Delay multiplier for exponential backoff
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504],  # Retry on these HTTP errors
)



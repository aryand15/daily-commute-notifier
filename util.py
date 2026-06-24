"""Module that exposes various utility functions."""

import requests
import time
import datetime


def fetch_with_retries(
    url: str,
    retries: int = 3,
    timeout: int = 10,
) -> dict:
    """
    Fetch JSON data with retry logic and exponential backoff.

    Args:
        url (str): URL to fetch.
        retries (int): Maximum retry attempts.
        timeout (int): Request timeout in seconds.

    Returns:
        dict: Parsed JSON response.

    Raises:
        RuntimeError: If all retry attempts fail.
    """
    last_exception = None

    for attempt in range(retries):
        try:
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()
            return response.json()

        except requests.RequestException as exc:
            last_exception = exc

            if attempt < retries - 1:
                time.sleep(2**attempt)

    raise RuntimeError(
        f"Failed to fetch weather data after {retries} attempts."
    ) from last_exception


def format_hour(dt: datetime) -> str:
    """
    Convert a datetime into a human-readable hour string.

    Example:
        2026-06-24 14:00 -> "2:00 PM"

    Args:
        dt (datetime): Datetime to format.

    Returns:
        str: Formatted hour string.
    """
    return dt.strftime("%I:00 %p").lstrip("0")
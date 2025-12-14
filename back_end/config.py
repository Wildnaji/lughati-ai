"""
Configuration module for Lughati AI backend.
Handles environment variables and settings.
"""
import os
from typing import Optional


def get_openai_api_key() -> str:
    """Get OpenAI API key from environment variable."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError(
            "OPENAI_API_KEY environment variable is not set. "
            "Please set it before running the application."
        )
    return api_key


def get_openai_model() -> str:
    """Get the OpenAI model to use. Defaults to gpt-4o-mini."""
    return os.getenv("OPENAI_MODEL", "gpt-4o-mini")


def get_api_timeout() -> int:
    """Get API timeout in seconds. Defaults to 60."""
    return int(os.getenv("API_TIMEOUT", "60"))



"""
Google Gemini client configuration.

This module configures the AsyncOpenAI client to use Google Gemini API.
"""

from openai import AsyncOpenAI

from ..config import settings


# Create Gemini client using OpenAI-compatible API
# Reference: https://ai.google.dev/gemini-api/docs/openai
gemini_client = AsyncOpenAI(
    api_key=settings.gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

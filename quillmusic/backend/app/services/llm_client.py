"""
LLM Client for QuillMusic

This module provides an abstraction layer for calling LLM APIs
in a structured, testable way.
"""
import json
import logging
from abc import ABC, abstractmethod
from typing import Optional, Any

logger = logging.getLogger(__name__)


class LLMClient(ABC):
    """Abstract base class for LLM clients."""

    @abstractmethod
    def generate_json(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4000,
    ) -> dict[str, Any]:
        """
        Generate a JSON response from the LLM.

        Args:
            prompt: The user prompt
            system_prompt: Optional system prompt to set context
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum tokens in response

        Returns:
            Parsed JSON dictionary from LLM response

        Raises:
            Exception: If LLM call fails or response is not valid JSON
        """
        pass


class OpenAICompatibleClient(LLMClient):
    """
    LLM client for OpenAI-compatible APIs.

    Works with OpenAI API, Azure OpenAI, and other compatible endpoints.
    """

    def __init__(
        self,
        api_key: str,
        model_name: str,
        api_base: Optional[str] = None,
    ):
        """
        Initialize the OpenAI-compatible client.

        Args:
            api_key: API key for authentication
            model_name: Name of the model to use
            api_base: Optional base URL for API (uses OpenAI default if None)
        """
        self.api_key = api_key
        self.model_name = model_name
        self.api_base = api_base

        try:
            from openai import OpenAI

            self.client = OpenAI(
                api_key=api_key,
                base_url=api_base,
            )
        except ImportError:
            raise ImportError(
                "openai package is required for LLM functionality. "
                "Install it with: pip install openai>=1.0.0"
            )

    def generate_json(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4000,
    ) -> dict[str, Any]:
        """Generate a JSON response from the LLM."""
        try:
            messages = []

            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})

            messages.append({"role": "user", "content": prompt})

            logger.info(
                f"Calling LLM API: model={self.model_name}, "
                f"temperature={temperature}, max_tokens={max_tokens}"
            )

            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                response_format={"type": "json_object"},
            )

            content = response.choices[0].message.content

            if not content:
                raise ValueError("LLM returned empty response")

            # Parse JSON
            result = json.loads(content)

            logger.info(f"Successfully generated JSON response with {len(result)} keys")

            return result

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {e}")
            raise ValueError(f"LLM did not return valid JSON: {e}")
        except Exception as e:
            logger.error(f"LLM API call failed: {e}")
            raise


class FakeLLMClient(LLMClient):
    """
    Fake LLM client for testing purposes.

    Returns predetermined responses without making actual API calls.
    """

    def __init__(self, mock_response: Optional[dict[str, Any]] = None):
        """
        Initialize the fake LLM client.

        Args:
            mock_response: Optional predefined response to return
        """
        self.mock_response = mock_response or {}

    def generate_json(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4000,
    ) -> dict[str, Any]:
        """Return the mock response."""
        logger.info("FakeLLMClient returning mock response")
        return self.mock_response


def create_llm_client(
    api_key: str,
    model_name: str,
    api_base: Optional[str] = None,
    provider: str = "openai-compatible",
) -> LLMClient:
    """
    Factory function to create an LLM client.

    Args:
        api_key: API key for authentication
        model_name: Name of the model to use
        api_base: Optional base URL for API
        provider: Provider type (currently only "openai-compatible" supported)

    Returns:
        An LLM client instance

    Raises:
        ValueError: If provider is not supported
    """
    if provider == "openai-compatible":
        return OpenAICompatibleClient(
            api_key=api_key,
            model_name=model_name,
            api_base=api_base,
        )
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")

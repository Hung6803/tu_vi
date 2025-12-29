# -*- coding: utf-8 -*-
"""
Xiaomi MiMo API client for AI-powered chart interpretation.
Compatible with OpenAI API format.
"""

import os
import json
import asyncio
from typing import Optional, Dict, List, AsyncIterator
from pathlib import Path

try:
    from openai import OpenAI, AsyncOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


# MiMo API configuration
MIMO_BASE_URL = "https://api.xiaomimimo.com/v1"
DEFAULT_MODEL = "mimo-v2-flash"


class MimoError(Exception):
    """Exception for MiMo API errors."""
    pass


class MimoClient:
    """
    Client for Xiaomi MiMo API using OpenAI-compatible interface.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: str = DEFAULT_MODEL,
        timeout: float = 300.0,
    ):
        """
        Initialize the MiMo client.

        Args:
            api_key: MiMo API key (defaults to MIMO_API_KEY env var)
            base_url: API base URL (defaults to MIMO_BASE_URL)
            model: Model to use (default: mimo-v2-flash)
            timeout: Request timeout in seconds
        """
        if not OPENAI_AVAILABLE:
            raise MimoError(
                "OpenAI library not installed. Run: pip install openai"
            )

        self.api_key = api_key or os.environ.get("MIMO_API_KEY")
        if not self.api_key:
            raise MimoError(
                "MiMo API key not provided. Set MIMO_API_KEY environment variable."
            )

        self.base_url = base_url or os.environ.get("MIMO_BASE_URL", MIMO_BASE_URL)
        self.model = model
        self.timeout = timeout

        # Initialize clients
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            timeout=self.timeout,
        )

        self.async_client = AsyncOpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            timeout=self.timeout,
        )

    def generate(
        self,
        user_prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False,
        thinking: bool = False,
    ) -> str:
        """
        Generate a response from MiMo.

        Args:
            user_prompt: The user's prompt/question
            system_prompt: System prompt for context
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum tokens in response (None = no limit)
            stream: Whether to stream the response
            thinking: Enable reasoning mode

        Returns:
            Generated response text
        """
        messages = []

        if system_prompt:
            messages.append({
                "role": "system",
                "content": system_prompt
            })

        messages.append({
            "role": "user",
            "content": user_prompt
        })

        try:
            if stream:
                return self._generate_stream(messages, temperature, max_tokens, thinking)

            # Build request params
            request_params = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
                "stream": False,
            }

            if max_tokens:
                request_params["max_tokens"] = max_tokens

            response = self.client.chat.completions.create(**request_params)
            return response.choices[0].message.content

        except Exception as e:
            raise MimoError(f"Error calling MiMo API: {e}")

    def _generate_stream(
        self,
        messages: List[Dict],
        temperature: float,
        max_tokens: Optional[int],
        thinking: bool,
    ) -> str:
        """
        Generate response with streaming.

        Returns accumulated text.
        """
        full_response = ""

        request_params = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "stream": True,
        }

        if max_tokens:
            request_params["max_tokens"] = max_tokens

        stream = self.client.chat.completions.create(**request_params)

        for chunk in stream:
            if chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                full_response += content
                print(content, end="", flush=True)

        print()  # New line after streaming
        return full_response

    async def generate_async(
        self,
        user_prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> str:
        """
        Generate response asynchronously.

        Args:
            user_prompt: The user's prompt/question
            system_prompt: System prompt for context
            temperature: Sampling temperature
            max_tokens: Maximum tokens

        Returns:
            Generated response text
        """
        messages = []

        if system_prompt:
            messages.append({
                "role": "system",
                "content": system_prompt
            })

        messages.append({
            "role": "user",
            "content": user_prompt
        })

        try:
            request_params = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
            }

            if max_tokens:
                request_params["max_tokens"] = max_tokens

            response = await self.async_client.chat.completions.create(**request_params)
            return response.choices[0].message.content

        except Exception as e:
            raise MimoError(f"Error calling MiMo API: {e}")

    async def generate_stream_async(
        self,
        user_prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> AsyncIterator[str]:
        """
        Generate response with async streaming.

        Yields:
            Response text chunks
        """
        messages = []

        if system_prompt:
            messages.append({
                "role": "system",
                "content": system_prompt
            })

        messages.append({
            "role": "user",
            "content": user_prompt
        })

        try:
            request_params = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
                "stream": True,
            }

            if max_tokens:
                request_params["max_tokens"] = max_tokens

            stream = await self.async_client.chat.completions.create(**request_params)

            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            raise MimoError(f"Error calling MiMo API: {e}")

    def estimate_tokens(self, text: str) -> int:
        """
        Estimate number of tokens in text.

        Args:
            text: Text to estimate tokens for

        Returns:
            Estimated token count
        """
        # Rough estimate: ~3 characters per token for mixed Vietnamese/English
        return len(text) // 3

    def get_model_info(self) -> Dict:
        """
        Get information about the current model.

        Returns:
            Dict with model information
        """
        return {
            "model": self.model,
            "base_url": self.base_url,
            "max_context": 262144,  # 256K tokens
            "supports_streaming": True,
            "supports_thinking": True,
        }


def create_mimo_client(api_key: Optional[str] = None) -> MimoClient:
    """
    Create MiMo client with optional API key.

    Args:
        api_key: Optional API key (defaults to env var)

    Returns:
        Configured MimoClient instance
    """
    return MimoClient(api_key=api_key)


# Convenience function for quick generation
def quick_generate(
    prompt: str,
    system: Optional[str] = None,
    api_key: Optional[str] = None,
    **kwargs
) -> str:
    """
    Quick function to generate a response.

    Args:
        prompt: User prompt
        system: System prompt
        api_key: Optional API key
        **kwargs: Additional arguments for generate()

    Returns:
        Generated response
    """
    client = MimoClient(api_key=api_key)
    return client.generate(prompt, system, **kwargs)

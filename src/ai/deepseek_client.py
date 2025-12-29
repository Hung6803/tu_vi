"""
DeepSeek API client for AI-powered chart interpretation.
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


# DeepSeek API configuration
DEEPSEEK_BASE_URL = "https://api.deepseek.com/v1"
DEFAULT_MODEL = "deepseek-chat"  # or "deepseek-reasoner" for more complex reasoning


class DeepSeekError(Exception):
    """Exception for DeepSeek API errors."""
    pass


class DeepSeekClient:
    """
    Client for DeepSeek API using OpenAI-compatible interface.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: str = DEFAULT_MODEL,
        timeout: float = 120.0,
    ):
        """
        Initialize the DeepSeek client.

        Args:
            api_key: DeepSeek API key (defaults to DEEPSEEK_API_KEY env var)
            base_url: API base URL (defaults to DEEPSEEK_BASE_URL env var or default)
            model: Model to use
            timeout: Request timeout in seconds
        """
        if not OPENAI_AVAILABLE:
            raise DeepSeekError(
                "OpenAI library not installed. Run: pip install openai"
            )

        self.api_key = api_key or os.environ.get("DEEPSEEK_API_KEY")
        if not self.api_key:
            raise DeepSeekError(
                "DeepSeek API key not provided. Set DEEPSEEK_API_KEY environment variable."
            )

        self.base_url = base_url or os.environ.get("DEEPSEEK_BASE_URL", DEEPSEEK_BASE_URL)
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
        max_tokens: int = 8000,
        stream: bool = False,
    ) -> str:
        """
        Generate a response from DeepSeek.

        Args:
            user_prompt: The user's prompt/question
            system_prompt: System prompt for context
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum tokens in response
            stream: Whether to stream the response

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
                return self._generate_stream(messages, temperature, max_tokens)

            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=False,
            )

            return response.choices[0].message.content

        except Exception as e:
            raise DeepSeekError(f"Error calling DeepSeek API: {e}")

    def _generate_stream(
        self,
        messages: List[Dict],
        temperature: float,
        max_tokens: int,
    ) -> str:
        """
        Generate response with streaming.

        Returns accumulated text.
        """
        full_response = ""

        stream = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
        )

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
        max_tokens: int = 8000,
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
            response = await self.async_client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )

            return response.choices[0].message.content

        except Exception as e:
            raise DeepSeekError(f"Error calling DeepSeek API: {e}")

    async def generate_stream_async(
        self,
        user_prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 8000,
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
            stream = await self.async_client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True,
            )

            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            raise DeepSeekError(f"Error calling DeepSeek API: {e}")

    def estimate_tokens(self, text: str) -> int:
        """
        Estimate number of tokens in text.

        This is a rough estimate - actual tokenization may differ.

        Args:
            text: Text to estimate tokens for

        Returns:
            Estimated token count
        """
        # Rough estimate: ~4 characters per token for English
        # Vietnamese/Chinese may have different ratios
        # Using conservative estimate of 3 chars per token for mixed content
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
            "max_context": 128000 if "deepseek" in self.model else 8000,
            "supports_streaming": True,
        }


def load_prompt(prompt_name: str) -> str:
    """
    Load a prompt template from file.

    Args:
        prompt_name: Name of prompt file (without .txt extension)

    Returns:
        Prompt template string
    """
    prompt_path = Path(__file__).parent.parent.parent / "config" / "prompts" / f"{prompt_name}.txt"

    if not prompt_path.exists():
        raise FileNotFoundError(f"Prompt file not found: {prompt_path}")

    with open(prompt_path, 'r', encoding='utf-8') as f:
        return f.read()


def create_client_from_config() -> DeepSeekClient:
    """
    Create DeepSeek client from configuration.

    Returns:
        Configured DeepSeekClient instance
    """
    config_path = Path(__file__).parent.parent.parent / "config" / "deepseek.yaml"

    config = {}
    if config_path.exists():
        try:
            import yaml
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f) or {}
        except ImportError:
            pass

    return DeepSeekClient(
        api_key=config.get("api_key"),
        model=config.get("model", DEFAULT_MODEL),
        timeout=config.get("timeout", 120.0),
    )


# Convenience function for quick generation
def quick_generate(
    prompt: str,
    system: Optional[str] = None,
    **kwargs
) -> str:
    """
    Quick function to generate a response.

    Args:
        prompt: User prompt
        system: System prompt
        **kwargs: Additional arguments for generate()

    Returns:
        Generated response
    """
    client = DeepSeekClient()
    return client.generate(prompt, system, **kwargs)

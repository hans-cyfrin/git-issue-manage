"""OpenRouter API client for AI-powered content rewriting."""

import requests
from typing import Optional
from ..utils.config import Config


class OpenRouterClient:
    """OpenRouter API client for content rewriting."""

    def __init__(self, config: Optional[Config] = None, api_key: Optional[str] = None, model: Optional[str] = None):
        """Initialize OpenRouter API client.

        Args:
            config: Configuration object. If provided, api_key and model are ignored.
            api_key: OpenRouter API key. Used only if config is None.
            model: Model to use. Used only if config is None.

        Raises:
            ValueError: If no API key is available.
        """
        if config:
            self.api_key = config.openrouter_api_key
            self.model = config.openrouter_model
        else:
            self.api_key = api_key or ""
            self.model = model or 'anthropic/claude-3.5-sonnet'

        self.base_url = "https://openrouter.ai/api/v1/chat/completions"

        if not self.api_key:
            raise ValueError("OpenRouter API key is required")

    def rewrite_content(self, prompt: str, temperature: float = 0.7, max_tokens: Optional[int] = None) -> Optional[str]:
        """Rewrite content using OpenRouter API.

        Args:
            prompt: The prompt to send to the AI model
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum tokens in response

        Returns:
            The rewritten content, or None if an error occurred
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/yourusername/git-issue-manager",
            "X-Title": "Git Issue Manager"
        }

        data = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": temperature
        }

        if max_tokens:
            data["max_tokens"] = max_tokens

        try:
            response = requests.post(self.base_url, headers=headers, json=data, timeout=60)
            response.raise_for_status()

            result = response.json()
            return result['choices'][0]['message']['content']

        except requests.exceptions.Timeout:
            print("Error: Request to OpenRouter API timed out")
            return None
        except requests.exceptions.RequestException as e:
            print(f"Error calling OpenRouter API: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_detail = e.response.json()
                    print(f"API Error Details: {error_detail}")
                except:
                    print(f"HTTP Status: {e.response.status_code}")
            return None
        except (KeyError, IndexError) as e:
            print(f"Error parsing OpenRouter response: {str(e)}")
            return None
        except Exception as e:
            print(f"Unexpected error during OpenRouter API call: {str(e)}")
            return None

    def get_model(self) -> str:
        """Get the current model being used.

        Returns:
            The current model name
        """
        return self.model

    def set_model(self, model: str) -> None:
        """Set the model to use for requests.

        Args:
            model: The model name to use
        """
        self.model = model

    def is_available(self) -> bool:
        """Check if the OpenRouter client is properly configured.

        Returns:
            True if the client has a valid API key
        """
        return bool(self.api_key)
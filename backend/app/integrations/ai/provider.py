from abc import ABC, abstractmethod

import litellm


class AIProvider(ABC):
    @abstractmethod
    def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> str: ...

    @property
    @abstractmethod
    def model_name(self) -> str: ...


class LiteLLMProvider(AIProvider):
    def __init__(
        self,
        model: str = "gpt-4o-mini",
        api_key: str | None = None,
        temperature: float = 0.3,
        max_tokens: int = 2048,
        timeout: int = 60,
    ):
        self._model = model
        self._temperature = temperature
        self._max_tokens = max_tokens
        self._timeout = timeout
        if api_key:
            litellm.api_key = api_key

    def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = litellm.completion(
            model=self._model,
            messages=messages,
            temperature=temperature if temperature is not None else self._temperature,
            max_tokens=max_tokens if max_tokens is not None else self._max_tokens,
            timeout=self._timeout,
        )
        return response.choices[0].message.content

    @property
    def model_name(self) -> str:
        return self._model

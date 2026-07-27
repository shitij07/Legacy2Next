from unittest.mock import patch, MagicMock

import pytest

from app.integrations.ai.provider import AIProvider, LiteLLMProvider


def test_ai_provider_abstract():
    with pytest.raises(TypeError):
        AIProvider()


def test_litellm_provider_init_defaults():
    provider = LiteLLMProvider()
    assert provider.model_name == "gpt-4o-mini"


def test_litellm_provider_init_custom():
    provider = LiteLLMProvider(
        model="claude-3-haiku",
        api_key="test-key",
        temperature=0.5,
        max_tokens=4096,
        timeout=120,
    )
    assert provider.model_name == "claude-3-haiku"


@patch("app.integrations.ai.provider.litellm")
def test_generate_success(mock_litellm):
    mock_response = MagicMock()
    mock_response.choices[0].message.content = "Generated content"
    mock_litellm.completion.return_value = mock_response

    provider = LiteLLMProvider(api_key="test-key")
    result = provider.generate("Test prompt", system_prompt="Be helpful.")

    assert result == "Generated content"
    mock_litellm.completion.assert_called_once()
    kwargs = mock_litellm.completion.call_args[1]
    assert kwargs["model"] == "gpt-4o-mini"
    assert len(kwargs["messages"]) == 2
    assert kwargs["messages"][0]["role"] == "system"
    assert kwargs["messages"][0]["content"] == "Be helpful."
    assert kwargs["messages"][1]["role"] == "user"
    assert kwargs["messages"][1]["content"] == "Test prompt"


@patch("app.integrations.ai.provider.litellm")
def test_generate_without_system_prompt(mock_litellm):
    mock_response = MagicMock()
    mock_response.choices[0].message.content = "Content"
    mock_litellm.completion.return_value = mock_response

    provider = LiteLLMProvider()
    result = provider.generate("Hello")

    assert result == "Content"
    kwargs = mock_litellm.completion.call_args[1]
    assert len(kwargs["messages"]) == 1
    assert kwargs["messages"][0]["role"] == "user"
    assert kwargs["messages"][0]["content"] == "Hello"


@patch("app.integrations.ai.provider.litellm")
def test_generate_overrides_default_temperature(mock_litellm):
    mock_response = MagicMock()
    mock_response.choices[0].message.content = "Content"
    mock_litellm.completion.return_value = mock_response

    provider = LiteLLMProvider(temperature=0.3)
    provider.generate("Hello", temperature=0.9)

    kwargs = mock_litellm.completion.call_args[1]
    assert kwargs["temperature"] == 0.9


@patch("app.integrations.ai.provider.litellm")
def test_generate_overrides_default_max_tokens(mock_litellm):
    mock_response = MagicMock()
    mock_response.choices[0].message.content = "Content"
    mock_litellm.completion.return_value = mock_response

    provider = LiteLLMProvider(max_tokens=2048)
    provider.generate("Hello", max_tokens=512)

    kwargs = mock_litellm.completion.call_args[1]
    assert kwargs["max_tokens"] == 512


@patch("app.integrations.ai.provider.litellm")
def test_generate_provider_error_propagates(mock_litellm):
    mock_litellm.completion.side_effect = Exception("API Error")

    provider = LiteLLMProvider()
    with pytest.raises(Exception, match="API Error"):
        provider.generate("Hello")


@patch("app.integrations.ai.provider.litellm")
def test_generate_timeout_propagates(mock_litellm):
    from litellm.exceptions import Timeout
    mock_litellm.completion.side_effect = Timeout(
        model="gpt-4o-mini", llm_provider="openai", message="Request timed out"
    )

    provider = LiteLLMProvider()
    with pytest.raises(Timeout):
        provider.generate("Hello")


@patch("app.integrations.ai.provider.litellm")
def test_generate_passes_timeout_to_litellm(mock_litellm):
    mock_response = MagicMock()
    mock_response.choices[0].message.content = "Content"
    mock_litellm.completion.return_value = mock_response

    provider = LiteLLMProvider(timeout=30)
    provider.generate("Hello")

    kwargs = mock_litellm.completion.call_args[1]
    assert kwargs["timeout"] == 30

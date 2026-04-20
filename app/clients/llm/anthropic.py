import anthropic as anthropic_sdk
from app.clients.llm.base import LLMClient, LLMResponse
from app.core.config import get_settings

_DEFAULT_MODEL = "claude-sonnet-4-6"


class AnthropicLLMClient(LLMClient):
    def __init__(self) -> None:
        s = get_settings()
        self._client = anthropic_sdk.AsyncAnthropic(api_key=s.anthropic_api_key)
        self._model = s.llm_model or _DEFAULT_MODEL

    @property
    def provider(self) -> str:
        return "anthropic"

    async def complete(self, system_prompt: str, user_message: str) -> LLMResponse:
        response = await self._client.messages.create(
            model=self._model,
            max_tokens=512,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}],
        )
        usage = response.usage
        return LLMResponse(
            content=response.content[0].text.strip(),
            model=self._model,
            provider=self.provider,
            input_tokens=usage.input_tokens,
            output_tokens=usage.output_tokens,
        )

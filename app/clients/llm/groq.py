from groq import AsyncGroq
from app.clients.llm.base import LLMClient, LLMResponse
from app.core.config import get_settings

_DEFAULT_MODEL = "llama3-8b-8192"


class GroqLLMClient(LLMClient):
    def __init__(self) -> None:
        s = get_settings()
        self._client = AsyncGroq(api_key=s.groq_api_key)
        self._model = s.llm_model or _DEFAULT_MODEL

    @property
    def provider(self) -> str:
        return "groq"

    async def complete(self, system_prompt: str, user_message: str) -> LLMResponse:
        response = await self._client.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
        )
        choice = response.choices[0]
        usage = response.usage
        return LLMResponse(
            content=choice.message.content.strip(),
            model=self._model,
            provider=self.provider,
            input_tokens=usage.prompt_tokens,
            output_tokens=usage.completion_tokens,
        )

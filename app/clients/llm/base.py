from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class LLMResponse:
    content: str
    model: str
    provider: str
    input_tokens: int
    output_tokens: int


class LLMClient(ABC):
    @abstractmethod
    async def complete(self, system_prompt: str, user_message: str) -> LLMResponse:
        ...

    @property
    @abstractmethod
    def provider(self) -> str:
        ...

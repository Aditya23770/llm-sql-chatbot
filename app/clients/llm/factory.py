from app.clients.llm.base import LLMClient


def get_llm_client(provider: str) -> LLMClient:
    if provider == "groq":
        from app.clients.llm.groq import GroqLLMClient
        return GroqLLMClient()
    if provider == "openai":
        from app.clients.llm.openai import OpenAILLMClient
        return OpenAILLMClient()
    if provider == "anthropic":
        from app.clients.llm.anthropic import AnthropicLLMClient
        return AnthropicLLMClient()
    raise ValueError(f"Unknown LLM provider: {provider!r}. Choose groq | openai | anthropic")

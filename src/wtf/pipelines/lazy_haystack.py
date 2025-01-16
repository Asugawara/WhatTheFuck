from dataclasses import dataclass, field
from typing import Any


@dataclass
class StreamingChunk:
    content: str
    meta: dict[str, Any] = field(default_factory=dict, hash=False)


class LazyHaystack:
    @staticmethod
    def import_secret():  # type: ignore
        from haystack.utils.auth import Secret

        return Secret

    @staticmethod
    def import_openai_generator():  # type: ignore
        from haystack.components.generators import OpenAIGenerator

        return OpenAIGenerator

    @staticmethod
    def import_anthropic_generator():  # type: ignore
        from haystack_integrations.components.generators.anthropic import AnthropicGenerator

        return AnthropicGenerator

    @staticmethod
    def import_vertex_ai_gemini_generator():  # type: ignore
        from haystack_integrations.components.generators.google_vertex import VertexAIGeminiGenerator

        return VertexAIGeminiGenerator

    @staticmethod
    def import_pipeline():  # type: ignore
        from haystack.core.pipeline import Pipeline

        return Pipeline

    @staticmethod
    def import_prompt_builder():  # type: ignore
        from haystack.components.builders.prompt_builder import PromptBuilder

        return PromptBuilder

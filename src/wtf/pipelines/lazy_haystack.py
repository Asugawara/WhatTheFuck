from dataclasses import dataclass, field
from typing import Any


@dataclass
class StreamingChunk:
    content: str
    meta: dict[str, Any] = field(default_factory=dict, hash=False)


class LazyHaystack:
    @staticmethod
    def import_secret():
        from haystack.utils.auth import Secret

        return Secret

    @staticmethod
    def import_haystack_converter_logger():
        from haystack.components.converters.html import logger

        return logger

    @staticmethod
    def import_openai_generator():
        from haystack.components.generators import OpenAIGenerator

        return OpenAIGenerator

    @staticmethod
    def import_anthropic_generator():
        from haystack_integrations.components.generators.anthropic import AnthropicGenerator

        return AnthropicGenerator

    @staticmethod
    def import_vertex_ai_gemini_generator():
        from haystack_integrations.components.generators.google_vertex import VertexAIGeminiGenerator

        return VertexAIGeminiGenerator

    @staticmethod
    def import_pipeline():
        from haystack.core.pipeline import Pipeline

        return Pipeline

    @staticmethod
    def import_prompt_builder():
        from haystack.components.builders.prompt_builder import PromptBuilder

        return PromptBuilder

    @staticmethod
    def import_output_adapter():
        from haystack.components.converters import OutputAdapter

        return OutputAdapter

    @staticmethod
    def import_link_content_fetcher():
        from haystack.components.fetchers import LinkContentFetcher

        return LinkContentFetcher

    @staticmethod
    def import_html_to_document():
        from haystack.components.converters.html import HTMLToDocument

        return HTMLToDocument

    @staticmethod
    def import_websearch():
        # NOTE: websearch.py imports haystack component, need to import it here
        from wtf.pipelines.components.websearch import WebSearch

        return WebSearch

from abc import ABCMeta, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass

from wtf.constants.models import ANTHROPIC_MODELS, OPENAI_MODELS, VERTEX_MODELS
from wtf.pipelines.lazy_haystack import LazyHaystack, StreamingChunk


@dataclass(frozen=True)
class LLMOutput:
    fixed_command: str
    content: str


class PipelineBase(metaclass=ABCMeta):
    @abstractmethod
    def run(self, command: str, command_output: str) -> LLMOutput: ...

    def _factory_generator(  # type: ignore
        self,
        model: str,
        openai_api_key: str = "",
        anthropic_api_key: str = "",
        streaming_callback: Callable[[StreamingChunk], None] | None = None,
    ):
        if model in OPENAI_MODELS:
            # NOTE: haystack modules are very slow to import.
            # To optimize, avoid importing unused modules and use lazy imports for the necessary ones.
            OpenAIGenerator = LazyHaystack.import_openai_generator()
            Secret = LazyHaystack.import_secret()

            return OpenAIGenerator(
                api_key=Secret.from_token(openai_api_key),
                model=model,
                streaming_callback=streaming_callback,
            )
        elif model in ANTHROPIC_MODELS:
            AnthropicGenerator = LazyHaystack.import_anthropic_generator()
            Secret = LazyHaystack.import_secret()

            return AnthropicGenerator(
                api_key=Secret.from_token(anthropic_api_key),
                model=model,
                streaming_callback=streaming_callback,
            )
        elif model in VERTEX_MODELS:
            VertexAIGeminiGenerator = LazyHaystack.import_vertex_ai_gemini_generator()

            return VertexAIGeminiGenerator(
                model=model,
                streaming_callback=streaming_callback,
            )
        else:
            raise NotImplementedError(f"Model {model} is not supported")

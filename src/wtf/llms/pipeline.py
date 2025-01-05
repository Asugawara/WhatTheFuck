import re
from collections.abc import Callable
from dataclasses import dataclass

from haystack import Pipeline
from haystack.components.builders.prompt_builder import PromptBuilder
from haystack.components.generators import OpenAIGenerator
from haystack.dataclasses import StreamingChunk
from haystack.utils import Secret
from haystack_integrations.components.generators.anthropic import AnthropicGenerator
from haystack_integrations.components.generators.google_vertex import VertexAIGeminiGenerator

from wtf.constants.models import ANTHROPIC_MODELS, OPENAI_MODELS, VERTEX_MODELS

RE_FIXED_COMMAND = re.compile(r"<FIXED>(.*)</FIXED>", re.IGNORECASE | re.DOTALL)


@dataclass(frozen=True)
class LLMOutput:
    fixed_command: str
    content: str


class CommandOutputAnalyzer:
    def __init__(
        self,
        prompt: str,
        model: str,
        openai_api_key: str = "",
        anthropic_api_key: str = "",
        streaming_callback: Callable[[StreamingChunk], None] | None = None,
    ) -> None:
        self._prompt = prompt
        self._model = model
        self._openai_api_key = Secret.from_token(openai_api_key) if openai_api_key else ""
        self._anthropic_api_key = Secret.from_token(anthropic_api_key) if anthropic_api_key else ""
        self._streaming_callback = streaming_callback

    def _factory_generator(self) -> OpenAIGenerator | AnthropicGenerator:
        if self._model in OPENAI_MODELS:
            return OpenAIGenerator(
                api_key=self._openai_api_key,
                model=self._model,
                streaming_callback=self._streaming_callback,
            )
        elif self._model in ANTHROPIC_MODELS:
            return AnthropicGenerator(
                api_key=self._anthropic_api_key,
                model=self._model,
                streaming_callback=self._streaming_callback,
            )
        elif self._model in VERTEX_MODELS:
            return VertexAIGeminiGenerator(
                model=self._model,
                streaming_callback=self._streaming_callback,
            )
        else:
            raise NotImplementedError(f"Model {self._model} is not supported")

    def _build_pipeline(self) -> Pipeline:
        pipe = Pipeline()
        pipe.add_component("command_output_prompt_builder", PromptBuilder(template=self._prompt))
        pipe.add_component("command_output_analyzer", self._factory_generator())
        pipe.connect("command_output_prompt_builder", "command_output_analyzer")
        return pipe

    def _parse_fixed_command(self, llm_output: str) -> str:
        match = RE_FIXED_COMMAND.search(llm_output)
        if match:
            return match.group(1).replace("\n", " ").strip(" `")
        return ""

    def run(self, command: str, command_output: str) -> LLMOutput:
        pipeline = self._build_pipeline()
        result = pipeline.run(
            {
                "command_output_prompt_builder": {
                    "command": command,
                    "command_output": command_output,
                }
            }
        )
        llm_output = result["command_output_analyzer"]["replies"][0]
        fixed_command = self._parse_fixed_command(llm_output)
        return LLMOutput(fixed_command=fixed_command, content=llm_output)

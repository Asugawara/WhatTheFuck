import re
from collections.abc import Callable
from dataclasses import dataclass

from wtf.constants.models import ANTHROPIC_MODELS, OPENAI_MODELS, VERTEX_MODELS
from wtf.llms.lazy_haystack import LazyHaystack, StreamingChunk

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
        self._openai_api_key = openai_api_key
        self._anthropic_api_key = anthropic_api_key
        self._streaming_callback = streaming_callback

    def _factory_generator(self):  # type: ignore
        if self._model in OPENAI_MODELS:
            # NOTE: haystack modules are very slow to import.
            # To optimize, avoid importing unused modules and use lazy imports for the necessary ones.
            OpenAIGenerator = LazyHaystack.import_openai_generator()  # type: ignore
            Secret = LazyHaystack.import_secret()  # type: ignore
            return OpenAIGenerator(
                api_key=Secret.from_token(self._openai_api_key),
                model=self._model,
                streaming_callback=self._streaming_callback,
            )
        elif self._model in ANTHROPIC_MODELS:
            AnthropicGenerator = LazyHaystack.import_anthropic_generator()  # type: ignore
            Secret = LazyHaystack.import_secret()  # type: ignore
            return AnthropicGenerator(
                api_key=Secret.from_token(self._anthropic_api_key),
                model=self._model,
                streaming_callback=self._streaming_callback,
            )
        elif self._model in VERTEX_MODELS:
            VertexAIGeminiGenerator = LazyHaystack.import_vertex_ai_gemini_generator()  # type: ignore

            return VertexAIGeminiGenerator(
                model=self._model,
                streaming_callback=self._streaming_callback,
            )
        else:
            raise NotImplementedError(f"Model {self._model} is not supported")

    def _build_pipeline(self):  # type: ignore
        Pipeline = LazyHaystack.import_pipeline()  # type: ignore
        PromptBuilder = LazyHaystack.import_prompt_builder()  # type: ignore

        pipe = Pipeline()
        pipe.add_component("command_output_prompt_builder", PromptBuilder(template=self._prompt))
        pipe.add_component("command_output_analyzer", self._factory_generator())  # type: ignore[no-untyped-call]
        pipe.connect("command_output_prompt_builder", "command_output_analyzer")
        return pipe

    def _parse_fixed_command(self, llm_output: str) -> str:
        match = RE_FIXED_COMMAND.search(llm_output)
        if match:
            return match.group(1).replace("\n", " ").strip(" `")
        return ""

    def run(self, command: str, command_output: str) -> LLMOutput:
        pipeline = self._build_pipeline()  # type: ignore
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

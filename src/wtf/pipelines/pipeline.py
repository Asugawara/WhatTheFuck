import re
from collections.abc import Callable

from wtf.pipelines.base import LLMOutput, PipelineBase
from wtf.pipelines.lazy_haystack import LazyHaystack, StreamingChunk

RE_FIXED_COMMAND = re.compile(r"<FIXED>(.*)</FIXED>", re.IGNORECASE | re.DOTALL)


class CommandOutputAnalyzer(PipelineBase):
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

    def _build_pipeline(self):  # type: ignore
        Pipeline = LazyHaystack.import_pipeline()
        PromptBuilder = LazyHaystack.import_prompt_builder()

        pipe = Pipeline()
        pipe.add_component("command_output_prompt_builder", PromptBuilder(template=self._prompt))
        pipe.add_component(
            "command_output_analyzer",
            self._factory_generator(
                self._model, self._openai_api_key, self._anthropic_api_key, self._streaming_callback
            ),
        )
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

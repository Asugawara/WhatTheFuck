import re
from collections.abc import Callable

from fake_useragent import UserAgent
from logzero import logger

from wtf.pipelines.base import LLMOutput, PipelineBase
from wtf.pipelines.lazy_haystack import LazyHaystack, StreamingChunk

RE_FIXED_COMMAND = re.compile(r"<FIXED>(.*)</FIXED>", re.IGNORECASE | re.DOTALL)


class CommandOutputAnalyzerWithSearch(PipelineBase):
    def __init__(
        self,
        search_query_prompt: str,
        prompt_with_websearch: str,
        model: str,
        openai_api_key: str = "",
        anthropic_api_key: str = "",
        streaming_callback: Callable[[StreamingChunk], None] | None = None,
        allowed_domains: tuple[str, ...] | None = None,
        use_playwright: bool = True,
        serper_api_key: str = "",
    ) -> None:
        self._search_query_prompt = search_query_prompt
        self._prompt_with_websearch = prompt_with_websearch
        self._model = model
        self._openai_api_key = openai_api_key
        self._anthropic_api_key = anthropic_api_key
        self._streaming_callback = streaming_callback
        self._allowed_domains = allowed_domains
        self._use_playwright = use_playwright
        self._serper_api_key = serper_api_key
        self._ua = UserAgent()

    def _build_pipeline(self):  # type: ignore
        Pipeline = LazyHaystack.import_pipeline()
        PromptBuilder = LazyHaystack.import_prompt_builder()
        OutputAdapter = LazyHaystack.import_output_adapter()
        LinkContentFetcher = LazyHaystack.import_link_content_fetcher()
        HTMLToDocument = LazyHaystack.import_html_to_document()
        html_logger = LazyHaystack.import_haystack_converter_logger()
        # NOTE: Haystack HTMLToDocument logger is too verbose
        html_logger.disabled = True
        if self._use_playwright:
            logger.debug("Use Playwright")
            WebSearch = LazyHaystack.import_websearch()
            websearch_instance = WebSearch(allowed_domains=self._allowed_domains, user_agent=self._ua.chrome)
        else:
            logger.debug("Use Serper")
            WebSearch = LazyHaystack.import_serper_websearch()
            Secret = LazyHaystack.import_secret()
            websearch_instance = WebSearch(
                api_key=Secret.from_token(self._serper_api_key), allowed_domains=self._allowed_domains
            )

        pipe = Pipeline()
        pipe.add_component("search_query_prompt_builder", PromptBuilder(template=self._search_query_prompt))
        pipe.add_component(
            "search_query_generator",
            self._factory_generator(self._model, self._openai_api_key, self._anthropic_api_key, None),
        )
        pipe.add_component("llm_output_adapter", OutputAdapter(template="{{ replies[0] }}", output_type=str))
        pipe.add_component("search_google", websearch_instance)
        pipe.add_component("link_content_fetcher", LinkContentFetcher(user_agents=[self._ua.chrome]))
        pipe.add_component("html_to_documents", HTMLToDocument(extraction_kwargs={"output_format": "markdown"}))
        pipe.add_component("command_output_prompt_builder", PromptBuilder(template=self._prompt_with_websearch))
        pipe.add_component(
            "command_output_analyzer",
            self._factory_generator(
                self._model, self._openai_api_key, self._anthropic_api_key, self._streaming_callback
            ),
        )

        pipe.connect("search_query_prompt_builder", "search_query_generator")
        pipe.connect("search_query_generator.replies", "llm_output_adapter")
        pipe.connect("llm_output_adapter", "search_google.query")
        pipe.connect("search_google.links", "link_content_fetcher.urls")
        pipe.connect("link_content_fetcher.streams", "html_to_documents.sources")
        pipe.connect("html_to_documents.documents", "command_output_prompt_builder.web_contents")
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
                "search_query_prompt_builder": {
                    "command": command,
                    "command_output": command_output,
                },
                "command_output_prompt_builder": {
                    "command": command,
                    "command_output": command_output,
                },
            },
        )
        llm_output = result["command_output_analyzer"]["replies"][0]
        fixed_command = self._parse_fixed_command(llm_output)
        return LLMOutput(fixed_command=fixed_command, content=llm_output)

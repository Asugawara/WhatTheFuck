from wtf.pipelines.base import PipelineBase
from wtf.pipelines.lazy_haystack import StreamingChunk
from wtf.pipelines.pipeline import CommandOutputAnalyzer
from wtf.pipelines.pipeline_with_search import CommandOutputAnalyzerWithSearch


def factroy_pipeline(
    prompt_path: str,
    model: str,
    openai_api_key: str = "",
    anthropic_api_key: str = "",
    with_websearch: bool = False,
    search_query_prompt_path: str = "",
    allowed_domains: tuple[str, ...] | None = None,
    use_playwright: bool = True,
    serper_api_key: str = "",
) -> PipelineBase:
    with open(prompt_path) as f:
        prompt_template = f.read()

    def streaming_callback(chunk: StreamingChunk) -> None:
        print(chunk.content, end="", flush=True)

    if with_websearch:
        with open(search_query_prompt_path) as f:
            search_query_prompt_template = f.read()

        return CommandOutputAnalyzerWithSearch(
            search_query_prompt=search_query_prompt_template,
            prompt_with_websearch=prompt_template,
            model=model,
            openai_api_key=openai_api_key,
            anthropic_api_key=anthropic_api_key,
            streaming_callback=streaming_callback,
            allowed_domains=allowed_domains,
            use_playwright=use_playwright,
            serper_api_key=serper_api_key,
        )
    return CommandOutputAnalyzer(
        prompt_template,
        model=model,
        openai_api_key=openai_api_key,
        anthropic_api_key=anthropic_api_key,
        streaming_callback=streaming_callback,
    )

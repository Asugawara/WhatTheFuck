from urllib.parse import urlparse

from haystack import component
from logzero import logger
from requests_html_playwright import HTMLSession


@component
class WebSearch:
    GOOGLE_SEARCH_BASEURL = "https://www.google.com/search"

    def __init__(
        self, allowed_domains: tuple[str, ...] | None = None, top_k: int = 10, user_agent: str = "", max_urls: int = 5
    ) -> None:
        self._allowed_domains = allowed_domains
        self._top_k = top_k
        self._max_urls = max_urls
        self._user_agent = user_agent

    @staticmethod
    def _is_allowed_url(url: str, allowed_domains: tuple[str, ...] | None) -> bool:
        if allowed_domains is None:
            logger.debug("No allowed domains")
            return True

        url_components = urlparse(url)
        if (
            url_components.netloc
            and allowed_domains
            and any(url_components.netloc in domain for domain in allowed_domains)
        ):
            return True
        logger.debug("Skip the url with netloc: %s", url_components.netloc)
        return False

    @component.output_types(links=list[str])  # type: ignore
    def run(self, query: str) -> dict[str, list[str]]:
        logger.debug("query: %s", query)
        with HTMLSession() as session:
            response = session.get(
                self.GOOGLE_SEARCH_BASEURL,
                params={"q": query},
                headers={"User-Agent": str(self._user_agent), "Referer": "https://www.google.com"},
            )
            response.html.render()

        links = []
        counter = 0
        for url in response.html.absolute_links:
            logger.debug("url: %s", url)
            if url.startswith(self.GOOGLE_SEARCH_BASEURL):
                logger.debug("Skip the search result page")
                continue
            if not self._is_allowed_url(url, self._allowed_domains):
                continue
            links.append(url)
            counter += 1
            if counter >= self._max_urls:
                break

        return {"links": links[: self._top_k]}

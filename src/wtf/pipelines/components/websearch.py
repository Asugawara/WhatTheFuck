from urllib.parse import urlparse

from haystack import component
from logzero import logger
from requests_html_playwright import HTMLSession


@component
class WebSearch:
    GOOGLE_SEARCH_BASEURL = "https://www.google.com/search"

    def __init__(self, available_netlocs: tuple[str, ...] | None = None, max_urls: int = 5) -> None:
        self._available_netlocs = available_netlocs
        self._max_urls = max_urls

    @component.output_types(urls=list[str])  # type: ignore
    def run(self, query: str) -> dict[str, list[str]]:
        logger.debug("query: %s", query)
        with HTMLSession() as session:
            response = session.get(self.GOOGLE_SEARCH_BASEURL, params={"q": query})
            response.html.render()

        urls = []
        counter = 0
        for url in response.html.absolute_links:
            logger.debug("url: %s", url)
            if url.startswith(self.GOOGLE_SEARCH_BASEURL):
                logger.debug("Skip the search result page")
                continue
            url_components = urlparse(url)
            if not url_components.netloc:
                continue
            if self._available_netlocs and url_components.netloc not in self._available_netlocs:
                logger.debug("Skip the url with netloc: %s", url_components.netloc)
                continue
            urls.append(url)
            counter += 1
            if counter >= self._max_urls:
                break

        return {"urls": urls}
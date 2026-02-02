"""Web Search skill using Brave Search API."""

from langchain_core.tools import tool
import structlog
from typing import Optional, List

import httpx

logger = structlog.get_logger(__name__)


class WebSearchSkill:
    """Skill for searching the web using Brave Search API."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize web search skill.

        Args:
            api_key: Brave Search API key (from environment if not provided)
        """
        import os
        self.api_key = api_key or os.getenv("BRAVE_API_KEY", "")
        self.base_url = "https://api.search.brave.com/res/v1/web/search"
        self.headers = {
            "Accept": "application/json",
            "X-Subscription-Token": self.api_key,
        }

    @tool
    def web_search(
        self,
        query: str,
        count: int = 10,
        country: str = "US",
        search_lang: str = "en",
        freshness: Optional[str] = None,
    ) -> str:
        """Search the web using Brave Search API.

        Args:
            query: Search query string
            count: Number of results (1-10)
            country: 2-letter country code for region-specific results
            search_lang: ISO language code for search results
            freshness: Filter by discovery time (pd=past day, pw=past week, pm=past month)

        Returns:
            Search results with titles, URLs, and snippets
        """
        if not self.api_key:
            return "Error: Brave API key not configured. Set BRAVE_API_KEY in .env file."

        if not query.strip():
            return "Error: Empty search query."

        params = {
            "q": query,
            "count": min(max(count, 1), 10),
            "country": country,
            "search_lang": search_lang,
        }

        if freshness:
            params["freshness"] = freshness

        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.get(
                    self.base_url,
                    headers=self.headers,
                    params=params,
                )
                response.raise_for_status()
                data = response.json()

            # Format results
            results = []
            web_results = data.get("web", {}).get("results", [])

            if not web_results:
                return "No results found."

            for i, result in enumerate(web_results[:count], 1):
                title = result.get("title", "No title")
                url = result.get("url", "")
                snippet = result.get("description", "")

                results.append(f"{i}. **{title}**\n   {url}\n   {snippet}\n")

            return "\n".join(results)

        except httpx.HTTPError as e:
            logger.error(f"Web search failed: {e}")
            return f"Error during search: {str(e)}"
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return f"Unexpected error: {str(e)}"

    @tool
    def web_fetch(self, url: str, extract_mode: str = "markdown", max_chars: int = 10000) -> str:
        """Fetch and extract readable content from a URL.

        Args:
            url: HTTP or HTTPS URL to fetch
            extract_mode: Extraction mode ("markdown" or "text")
            max_chars: Maximum characters to return

        Returns:
            Extracted content from the page
        """
        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.get(url, follow_redirects=True)
                response.raise_for_status()

            # Simple extraction - return first N chars
            content = response.text[:max_chars]
            return content

        except httpx.HTTPError as e:
            logger.error(f"Web fetch failed: {e}")
            return f"Error fetching URL: {str(e)}"
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return f"Unexpected error: {str(e)}"

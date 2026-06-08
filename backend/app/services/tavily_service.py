import logging
from typing import Optional
from app.config.settings import settings

logger = logging.getLogger("researchmind.tavily")

class TavilyService:
    def __init__(self):
        self.api_key = settings.TAVILY_API_KEY
        self.client = None
        if self.api_key:
            try:
                from tavily import TavilyClient
                self.client = TavilyClient(api_key=self.api_key)
            except Exception as e:
                logger.warning(f"Tavily client init failed: {e}")

    def search_web(self, topic: str, max_results: int = 10) -> list:
        """Search the web for a given topic and return structured results."""
        if not self.client:
            logger.warning("Tavily not configured, returning mock data.")
            return self._mock_results(topic)
        try:
            response = self.client.search(
                query=topic,
                search_depth="advanced",
                max_results=max_results,
                include_answer=True,
            )
            results = []
            for r in response.get("results", []):
                results.append({
                    "title": r.get("title", ""),
                    "url": r.get("url", ""),
                    "content": r.get("content", ""),
                    "source": r.get("url", "").split("/")[2] if r.get("url") else "",
                    "score": r.get("score", 0.0),
                })
            return results
        except Exception as e:
            logger.error(f"Tavily search error: {e}")
            return self._mock_results(topic)

    def _mock_results(self, topic: str) -> list:
        return [
            {"title": f"Overview of {topic}", "url": "https://example.com/1", "content": f"Comprehensive overview of {topic} including key trends and insights.", "source": "example.com", "score": 0.95},
            {"title": f"Latest Trends in {topic}", "url": "https://research.org/2", "content": f"Recent developments and future projections for {topic}.", "source": "research.org", "score": 0.90},
            {"title": f"{topic}: A Deep Dive", "url": "https://academic.edu/3", "content": f"Academic analysis and evidence-based review of {topic}.", "source": "academic.edu", "score": 0.85},
        ]

tavily_service = TavilyService()

import os


def web_search(query: str, n: int = 5):
    if os.getenv("LLM_PROVIDER", "mock").lower() == "mock":
        return [{"title": "(demo)", "body": "Offline demo mode: no web search performed.", "href": ""}]
    try:
        try:
            from ddgs import DDGS
        except ImportError:
            from duckduckgo_search import DDGS
        return list(DDGS().text(query, max_results=n))
    except Exception:
        return []

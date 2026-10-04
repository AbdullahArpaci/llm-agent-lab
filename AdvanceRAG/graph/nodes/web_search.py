from typing import Any, Dict
from langchain_core.documents import Document
from langchain_tavily import TavilySearch
from graph.state import GraphState

web_search_tool = TavilySearch(max_results=3)


def web_search(state: GraphState) -> Dict[str, Any]:
    """Search the web for the question and add the results to the documents."""
    print("---WEB SEARCH---")

    question = state["question"]
    documents = state.get("documents") or []

    results = web_search_tool.invoke({"query": question})["results"]
    web_results = Document(page_content="\n".join(r["content"] for r in results))

    return {"question": question, "documents": documents + [web_results]}
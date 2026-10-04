from ingestion import retriever
from typing import Dict,Any
from graph.state import GraphState

def retrieve(state: GraphState) -> Dict[str, Any]:
    print("----Retrieving----")
    question = state["question"]
    documents = retriever.invoke(question)

    return {"question": question, "documents": documents}
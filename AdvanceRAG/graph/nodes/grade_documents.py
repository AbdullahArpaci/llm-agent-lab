from typing import Dict,Any
from graph.chains.retrieval_grader import retriever_grader
from graph.state import GraphState

def grade_documents(state: GraphState) -> Dict[str, Any]:
    """
    Determines whether the retriever documents are relevant in the question
    if any document is not relevant,as will set a flag to run web search

    Args:
        state (dict): The current state of the graph

    Returns:
        state (dict): Filtered out irrelevant documents and updated web_search state
    """

    print("----Check documents relevant to questions----")

    question = state["question"]
    documents = state["documents"]
    filtered_documents = []
    web_search = False

    for d in documents:
        score = retriever_grader.invoke(
            {"question" : question, "document" : d.page_content}
        )

        grade = score.binary_score

        if grade.lower() == "yes":
            filtered_documents.append(d)
            print("-----GRADE: DOCUMENTS RELEVANT")
        else:
            print("-----GRADE: DOCUMENTS NOT RELEVANT")
            web_search = True
            continue

    return {"question" : question, "documents" : filtered_documents, "web_search" : web_search}

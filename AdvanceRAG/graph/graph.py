from dotenv import load_dotenv
load_dotenv()

from graph.node_constants import RETRIEVE, WEBSEARCH, GENERATE, GRADE_DOCUMENTS
from graph.nodes import generate,grade_documents,web_search,retrieve
from graph.chains.router import question_router,RouteQuery
from graph.state import GraphState
from graph.chains.hallucination_grader import hallucination_grader
from graph.chains.answer_grader import answer_chain
from langgraph.graph import END, StateGraph ,START

def decide_to_generate(state: GraphState):
    print("----ASSESS GRADED DCOUMENTS----")
    if state["web_search"]:
        print("WEBSEARCH")
        return WEBSEARCH
    else:
        return GENERATE

def grade_generation_grounded_in_documents_and_questions(state: GraphState):
    print("CHECK HALLUCINATION")

    question = state["question"]
    documents = state["documents"]
    generation = state["generation"]

    score = hallucination_grader.invoke(
        {"generation": generation, "document": documents}
    )

    if hallucination_grade := score.binary_score:
        print("GENERATION IS GROUNDED IN DOCUMENTS")
        score = answer_chain.invoke(
            {"question": question, "generation": generation})
        if answer_grade := score.binary_score:
                print("GENERATION ADDRESSED QUESTION")
                return "useful"
        else:
            print("GENERATION DOES NOT ADDRESS QUESTION")
            return "not useful"
    else:
        print("GENERATION IS NOT GROUNDED IN DOCUMENTS")
        return "not supported"


def route_question(state: GraphState) -> str:
    print("ROUTE QUESTION")

    question = state["question"]
    source = question_router.invoke({"questions": question})

    if source.datasource == "websearch":
        print("WEBSEARCH")
        return WEBSEARCH
    elif source.datasource == "vectorstore":
        print("VECTORSTORE")
        return RETRIEVE





workflow = StateGraph(GraphState)


workflow.add_node(RETRIEVE,retrieve)
workflow.add_node(GRADE_DOCUMENTS,grade_documents)
workflow.add_node(GENERATE,generate)
workflow.add_node(WEBSEARCH,web_search)


workflow.set_conditional_entry_point(
    route_question,
    {
        WEBSEARCH: WEBSEARCH,
        RETRIEVE: RETRIEVE,
    }
)

workflow.add_edge(RETRIEVE,GRADE_DOCUMENTS)

workflow.add_conditional_edges(
    GRADE_DOCUMENTS,
    decide_to_generate,
    {
     WEBSEARCH: WEBSEARCH,
     GENERATE: GENERATE,
    }
)

workflow.add_conditional_edges(
    GENERATE,
    grade_generation_grounded_in_documents_and_questions,
    {
        "not supported":GENERATE,
        "useful" : END,
        "not useful": WEBSEARCH,
    }
)

workflow.add_edge(
    WEBSEARCH,
    GENERATE
)

app = workflow.compile()

app.get_graph().draw_mermaid_png(output_file_path="graph.png")


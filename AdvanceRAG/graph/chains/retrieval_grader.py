from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from pydantic import BaseModel, Field


llm = ChatGoogleGenerativeAI(model = "gemini-3.6-flash",temperature = 0)

class GradeDocuments(BaseModel):
    """Binary score for relevance check on retrieved documents"""

    binary_score: str = Field(
        description="Documents are relevevent to the question. 'yes' or 'no' "
    )




structured_llm_grader = llm.with_structured_output(GradeDocuments)

system_prompt = """
You are a grader assessing whether an LLM generation is grounded in / supported by a set of retrieved facts. \n
Give a binary score 'yes' or 'no'. 'Yes' means that the answer is grounded in / supported by the set of facts.
"""
human_prompt = """
Retrieved document: {document} User question: {question}
"""

grade_prompt = ChatPromptTemplate.from_messages(
    [
        ("system",system_prompt),
        ("human",human_prompt),
    ]
)

retriever_grader = grade_prompt | structured_llm_grader

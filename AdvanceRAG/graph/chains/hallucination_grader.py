from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from pydantic import BaseModel, Field


llm = ChatGoogleGenerativeAI(model = "gemini-3.6-flash")


class GradeHallucinations(BaseModel):
    """Binary score for hallucination present in generated answer"""


    binary_score: bool = Field(
        description="Answer is grounded in the facts, 'yes' or 'no' ",
    )


structured_llm_grader = llm.with_structured_output(GradeHallucinations)


system_prompt = """
You are a grader assessing whether an LLM generation is grounded in / supported by a set of retrieved facts. \n
Give a binary score 'yes' or 'no'. 'Yes' means that the answer is grounded in / supported by the set of facts.
"""

human_prompt = """
Retrieved document: {document} \n LLM generation: {generation}
"""

prompt = ChatPromptTemplate.from_messages(
    [
        ("system",system_prompt),
        ("human",human_prompt)
    ]
)

hallucination_grader = prompt | structured_llm_grader
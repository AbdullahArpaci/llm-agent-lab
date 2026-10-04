from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel,Field
from langchain_core.prompts import PromptTemplate,ChatPromptTemplate


class AnswerGrader(BaseModel):

    binary_score : bool = Field(description="Answer addresses the question, 'yes' or 'no'")

llm = ChatGoogleGenerativeAI(model = "gemini-3.6-flash")

structured_llm_grader = llm.with_structured_output(AnswerGrader)
system_prompt = """
You are a grader assessing whether an answer addresses / resolves a question \n 
Give a binary score 'yes' or 'no'. Yes' means that the answer resolves the question.
"""

human_prompt = """
User question: \n\n {question} \n\n LLM generation: {generation}
"""
prompt = ChatPromptTemplate.from_messages(
    [
        ("system",system_prompt),
        ("human",human_prompt),
    ]
)


answer_chain = prompt | structured_llm_grader
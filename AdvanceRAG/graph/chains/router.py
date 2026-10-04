from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from pydantic import BaseModel, Field
from typing import Literal


class RouteQuery(BaseModel):
    """
    Route a user query to the most relevant datasource
    """

    datasource : Literal["vectorstore","websearch"] = Field(
        default = ...,
        description = "Given a user question choose to route it to web search or a vectorstore"
    )


llm = ChatGoogleGenerativeAI(model="gemini-3.6-flash",temperature = 0)
structured_llm_router = llm.with_structured_output(RouteQuery)

system_prompt = """
You are an expert at routing a user question to a vectorstore or web search.\n \n
The vectorstore contains documents related to agents,prompt engineering and adversarial attacks. \n \n
Use the vectorstore for questions on these topics.For all else,use web-search.
"""

route_prompt = ChatPromptTemplate.from_messages(
    [
        ("system",system_prompt),
        ("human", "{questions}")
    ]
)

question_router = route_prompt | structured_llm_router


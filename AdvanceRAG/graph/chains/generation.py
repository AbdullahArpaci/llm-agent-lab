from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser



llm = ChatGoogleGenerativeAI(model = "gemini-3.6-flash")


prompt_template = """
You are an assistant for question-answering tasks. Use the following pieces of retrieved context to answer the question. If you don't know the answer, just say that you don't know. Use three sentences maximum and keep the answer concise.
Question: {question} 
Context: {context} 
Answer:
"""

prompt = PromptTemplate.from_template(prompt_template)

generation_chain = prompt | llm | StrOutputParser()

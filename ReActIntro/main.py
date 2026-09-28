from dotenv import load_dotenv
load_dotenv()
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_tavily import TavilySearch
from langchain_classic.agents import create_react_agent, AgentExecutor

template = """Answer the following questions as best you can. You have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Previous conversation:
{chat_history}

Begin!

Question: {input}
Thought:{agent_scratchpad}"""

prompt = PromptTemplate.from_template(template)

llm = ChatGoogleGenerativeAI(model="gemini-3.6-flash")
search = TavilySearch(max_results=2)
tools = [search]

agent = create_react_agent(llm, tools, prompt)
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    handle_parsing_errors=True,
    max_iterations=5,
)

if __name__ == "__main__":
    chat_history = []
    while True:
        user_input = input("> ")
        if user_input.lower() in ("exit", "quit"):
            break
        result = agent_executor.invoke({
            "input": user_input,
            "chat_history": "\n".join(chat_history),
        })
        print(result["output"])
        chat_history.append(f"Human: {user_input}")
        chat_history.append(f"AI: {result['output']}")
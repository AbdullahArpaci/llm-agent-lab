from dotenv import load_dotenv
load_dotenv()
from langchain_tavily import TavilySearch
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from langchain.agents import create_agent
from langgraph.checkpoint.sqlite import SqliteSaver
from datetime import datetime
from langchain_core.tools import tool


search = TavilySearch(max_results=2)
llm = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite",thinking_level="low")

@tool
def simdiki_zaman() -> str:
    """Şu anki tarihi, günü ve saati döndürür.
    Kullanıcı bugünün tarihini, hangi gün olduğunu ya da saati sorduğunda kullan."""
    return datetime.now().strftime("%d.%m.%Y, %A, %H:%M")

tools = [search, simdiki_zaman]

if __name__ == "__main__":
    with SqliteSaver.from_conn_string("memory.db") as memory:
        agent = create_agent(model=llm,
                             tools=tools,
                             checkpointer=memory,
                             system_prompt="İlk arama soruyu cevaplıyorsa tekrar arama yapma."
                                            "En fazla 2 arama yap.")
        config = {
            "configurable": {"thread_id": "abc123"}
        }

        while True:
            user_input = input("> ")
            for msg, meta in agent.stream(
                    {"messages": [HumanMessage(content=user_input)]},
                    config=config,
                    stream_mode="messages",
            ):
                if meta["langgraph_node"] == "model":
                    print(msg.text, end="", flush=True)
            print()

import rclpy
from rclpy.node import Node
from swarm_talk_interfaces.srv import Takeoff
import time
from std_srvs.srv import Trigger
import threading

from dotenv import load_dotenv
load_dotenv()
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain.agents import create_agent
from datetime import datetime
from langchain_core.tools import tool
from langgraph.checkpoint.sqlite import SqliteSaver

llm = ChatGoogleGenerativeAI(model="gemini-3.6-flash", temperature=0)


system_prompt = """You are an operator assistant controlling a swarm of 3 drones in a Gazebo simulation. You carry out the user's natural-language commands by calling the provided tools.

Core rules:
- You can only command the drones through tools. Never claim an action was done unless you called a tool and it returned success.
- All distances and altitudes are in meters; altitude is height above ground.
- If the user asks for something no tool can do (e.g. formations, moving a single drone), say clearly that you cannot do it yet.

Ambiguous commands:
- If a command needs a number but does not give one ("rise a bit", "go higher"), do not guess. Ask the user how many meters.

Rejected or failed requests:
- If a tool rejects a request or fails, briefly explain the reason given in the tool's message.
- Never retry a rejected request with parameters you changed yourself. For example, if 100 m is rejected, do NOT retry with 30 m; tell the user the allowed range and ask what they want.
- If some drones succeeded and others failed, say which ones failed and why.

Multi-step commands:
- For commands like "take off and then land", run the steps in order. If a step fails, stop and report.

Safety:
- If the user says "stop", "emergency", "land" (in any language, e.g. "dur", "acil", "in"), call the land tool immediately without asking anything.

Response style:
- Always reply in Turkish, briefly. Summarize the result per drone in one or two sentences."""


class AgentNode(Node):
    def __init__(self):
        super().__init__("agent_node")
        self.takeoff_cli = self.create_client(Takeoff, "/swarm/takeoff")
        self.land_cli = self.create_client(Trigger, "/swarm/land")

    def call(self, client, request, timeout=20.0):
        if not client.wait_for_service(timeout_sec=2.0):
            return "Hata: sürü yöneticisine ulaşılamadı."
        future = client.call_async(request)
        deadline = time.monotonic() + timeout
        while not future.done():
            if time.monotonic() > deadline:
                return "Hata: zaman aşımı."
            time.sleep(0.05)
        res = future.result()
        return f"{'Başarılı' if res.success else 'Başarısız'}: {res.message}"


node = None  # main'de oluşturulacak; araçlar buna erişir


@tool
def swarm_takeoff(altitude: float) -> str:
    """Tüm sürüyü yerden belirtilen irtifaya (metre) kaldırır.
    İzin verilen aralık 1-30 metre. Drone'lar yerdeyken kullan."""
    req = Takeoff.Request()
    req.altitude = altitude
    return node.call(node.takeoff_cli, req)

@tool
def swarm_land() -> str:
    """Tüm drone'ları bulundukları yere indirir. Parametre almaz.
    Kullanıcı inmek, durmak, iptal etmek istediğinde ya da bir acil durum
    belirttiğinde bu aracı kullan."""
    req = Trigger.Request()
    return node.call(node.land_cli, req)

tools = [swarm_land,swarm_takeoff]
def main(args = None):
    global node
    rclpy.init(args=args)
    node = AgentNode()
    spin_thread = threading.Thread(target=rclpy.spin, args=(node,), daemon=True)
    spin_thread.start()

    with SqliteSaver.from_conn_string("memory.db") as memory:
        agent = create_agent(model=llm,
                            tools=tools,
                            checkpointer=memory,
                            system_prompt=system_prompt)
        config = {
            "configurable": {"thread_id": datetime.now().strftime("%Y%m%d-%H%M%S")}
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


if __name__ == "__main__":
    main()
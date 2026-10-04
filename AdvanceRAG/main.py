# main.py (proje kökünde)
from dotenv import load_dotenv
load_dotenv()
from graph.graph import app

if __name__ == "__main__":
    print(app.invoke({"question": "What is the current weather in Konya?"}))


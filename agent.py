"""Hello-world ReAct agent for scout-agent.

The whole point: we never call the tool ourselves. We hand the question and the
tool to the agent, and the LLM decides — on its own — to call it, reads the
result, and then answers. That decision loop is what makes this an agent and
not a pipeline.

Run:  python agent.py
"""

import os

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI

from tools import injury_tool

load_dotenv()

# Same single line as the smoke test — the model is swappable config.
llm = ChatGoogleGenerativeAI(model=os.environ["GEMINI_MODEL"])

# create_agent wires the Reason -> Act -> Observe loop for us: it binds the
# tools to the LLM, runs the model, executes any tool calls it asks for, feeds
# the results back, and repeats until the model answers without a tool.
agent = create_agent(llm, tools=[injury_tool])

question = "Is Luka Doncic available to play right now? Briefly justify."

# stream_mode="values" yields the full message list after each step, so we can
# watch the conversation grow: human -> AI (tool call) -> tool result -> AI
# (final answer). Printing the last message of each step shows the loop.
for step in agent.stream({"messages": [("user", question)]}, stream_mode="values"):
    step["messages"][-1].pretty_print()

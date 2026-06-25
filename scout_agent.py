"""The scout agent: one agent, two capability families, dynamic routing.

Day 2 gave the agent one mock tool and watched it decide to call it. Day 3 gave
it a database and watched it write its own SQL. Both were single-purpose demos.
This is the milestone they were building toward: ONE agent that holds BOTH
families at once and routes per question — the part that makes this an agent and
not a pipeline.

Capability families:
  - injury tool ........ live injury/availability lookup (mock for now)
  - list/describe/run .. read-only window onto the stats SQL database

The whole point is the CHOICE. So the system prompt deliberately does NOT
prescribe an order (unlike sql_agent.py). It tells the model what it can reach
for and leaves the routing to the LLM. Then we ask three questions that force
three different routes:
  - a stats question        -> the SQL tools only
  - an availability question -> the injury tool only
  - a mixed question        -> both, in whatever order the model picks

    .venv/bin/python scout_agent.py
"""

import os

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI

from sql_tools import describe_tables, list_tables, run_sql
from tools import injury_tool

load_dotenv()

# Same single swappable line as every other entry point. Never hardcode the id.
llm = ChatGoogleGenerativeAI(model=os.environ["GEMINI_MODEL"])

# NOTE: no prescribed sequence. The prompt names the two families and tells the
# model to decide which one(s) a question needs and in what order. That choice
# is the feature being demonstrated, so prescribing it would defeat the point.
SYSTEM_PROMPT = """You are a basketball scouting analyst. You answer questions \
about players using two independent capabilities, and your main job is to decide \
— per question — which one(s) you actually need:

1. A live injury and availability lookup. Use it for anything about whether a
   player is injured, healthy, out, or available to play right now.

2. A read-only SQL database of player stats. Use it for any number, average, or
   factual record. You do NOT know its schema in advance: list the tables, read
   the schema of the relevant ones, then write a single SELECT to fetch the
   answer.

Rules:
- Use one tool, the other, or both, in whatever order genuinely answers the
  question. Do not call a tool you don't need.
- Never assume the database contents and never guess a player's status. Go look.
- Base your final answer only on what the tools returned, and answer in plain
  English."""

agent = create_agent(
    llm,
    tools=[injury_tool, list_tables, describe_tables, run_sql],
    system_prompt=SYSTEM_PROMPT,
)

# Three questions engineered to force three different routes. We run them one at
# a time so we can watch the model's tool choices change with the question.
QUESTIONS = [
    # Stats only -> the model should never touch the injury tool.
    "How many points per game does Luka Doncic average this season (2025-26)?",
    # Availability only -> the model should never touch the SQL tools.
    "Is Luka Doncic available to play right now? Briefly justify.",
    # Mixed -> the model must reach for BOTH families, in the order it chooses.
    "Give me a quick read on Luka Doncic: how he's performing and whether he's "
    "available to play.",
]

for i, question in enumerate(QUESTIONS, 1):
    print(f"\n{'=' * 70}\nQUESTION {i}: {question}\n{'=' * 70}")
    for step in agent.stream(
        {"messages": [("user", question)]}, stream_mode="values"
    ):
        step["messages"][-1].pretty_print()

"""A text-to-SQL ReAct agent over the toy basketball database.

Ask a question in plain English; the agent discovers the schema and writes
its own SQL to answer it. Watch the streamed steps to see the ReAct loop:
it lists tables, inspects the schema, writes a SELECT (a JOIN!), observes
the rows, and only then answers.

    .venv/bin/python sql_agent.py
"""

import os

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI

from sql_tools import list_tables, describe_tables, run_sql

load_dotenv()

# The system prompt teaches the agent the METHOD, not the answer. It never
# hardcodes table or column names — the agent must discover them via the tools.
SYSTEM_PROMPT = """You are a basketball analyst with read-only access to a SQL database.

To answer a question about players or stats, always work in this order:
1. Call list_tables to see what tables exist.
2. Call describe_tables on the relevant ones to learn their columns and how
   they relate (foreign keys).
3. Write a single SQL SELECT and run it with run_sql.

Only read data with SELECT. If a query errors, read the message, fix the SQL,
and retry. Base your final answer only on the rows you actually retrieved."""

llm = ChatGoogleGenerativeAI(model=os.environ["GEMINI_MODEL"])
agent = create_agent(
    llm,
    tools=[list_tables, describe_tables, run_sql],
    system_prompt=SYSTEM_PROMPT,
)

question = "How many points per game does Luka Doncic average this season (2025-26)?"

for step in agent.stream(
    {"messages": [("user", question)]}, stream_mode="values"
):
    step["messages"][-1].pretty_print()

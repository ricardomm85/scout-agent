"""Smoke test: can we reach Gemini and get a reply?

No agent, no tools yet. This isolates ONE question — is the plumbing
(API key + model id + network) working? — before we add the agent loop
on top. If this prints text from Gemini, the foundation is solid.

Run:  python smoke_test.py
"""

import os

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

# Load .env into the process environment. langchain-google-genai reads
# GOOGLE_API_KEY from there automatically — we never pass the key in code.
load_dotenv()

# Model id lives in the environment, not hardcoded: swapping test vs prod
# models is a config change, not a code change.
model_name = os.environ["GEMINI_MODEL"]

# The "single line that changes per provider". Everything we build on top
# (the agent, the tools) stays the same regardless of which LLM sits here.
llm = ChatGoogleGenerativeAI(model=model_name)

# A plain question. No tools bound — we just want to confirm it answers.
response = llm.invoke("Reply in one short sentence: are you there?")

# In langchain-core 1.x, .content can be a list of structured blocks, not a
# plain string. .text flattens it to just the text — use that for display.
print(f"[{model_name}] {response.text}")

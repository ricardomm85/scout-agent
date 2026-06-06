# CLAUDE.md

Project context for Claude Code. Read this before touching anything.

## What this is

**scout-agent** is an AI agent system for **basketball scouting**. The goal:
given a player (e.g. "Luka Doncic"), the agent researches live sources (websites,
X/Twitter, YouTube, local press) and writes a **scouting report** aimed at
coaches and sporting directors.

It is not a static LLM answering from memory. It is a **ReAct agent** (Reason +
Act) that reasons, decides which tool to use, runs it, observes the result, and
reasons again — in a loop — until the report is complete.

We build it **in public**: every milestone is documented for LinkedIn posts and
the README. Documentation clarity is a goal, not an extra.

## Current status

**Day 0.** Only the base scaffolding exists (this file, README, docs). No agent
code yet. Next planned step: the agent "Hello World" — a ReAct agent with one
mock tool (`create_react_agent` + a medical-history tool). See the design
conversation and `docs/`.

## Target architecture

```
User / API  ──>  Orchestrator (LLM, central node)  <──>  Tools (scrapers)
                       │                                   - stats
                       │ (conditional edges)               - injuries / news
                       ▼                                   - contracts / salaries
                  Write report                             - YouTube transcripts
```

- **ReAct loop, not a linear pipeline.** The LLM routes dynamically: it requests
  a tool, observes, and decides whether it needs another or can write the report.
  No fixed sequences.
- **Thread-based memory.** LangGraph checkpointer + `thread_id` so we can iterate
  on an already-generated report (e.g. correct a mix-up between two players with
  the same name) like in a chat. In-memory for tests; SQLite/Postgres in prod.

## Stack

- **Language:** Python 3.13.
- **Agent framework:** LangGraph (`langgraph`, `langchain-anthropic`).
- **LLM:** Claude (Anthropic). Default model when coding: the most capable
  available in the 4.x family. Do NOT copy model IDs from old internet examples —
  verify the current ID before hardcoding it.
- **Scraping:** `httpx`/`requests`, BeautifulSoup, Playwright (for JS and light
  paywalled press). `pandas` for stat tables.
- **API:** FastAPI + uvicorn. Endpoint `POST /api/generate-report`.
- **Real time:** SSE (Server-Sent Events) to stream the agent's "thinking" to the
  frontend (reports take 15–30s). Celery/Redis if a background task queue is
  needed.
- **Deployment:** Docker + **Kamal** (push from local/CI over SSH to a VPS).
  Traefik as reverse proxy + Let's Encrypt.

## Conventions

- **Language:** everything in English — code, comments, and docs. Tool docstrings
  are CRITICAL: they are what the LLM reads to decide when to invoke each tool.
- **Tools = pure, testable functions.** Each scraper must run and be testable in
  isolation, without the agent. Write the function first, then wrap it with
  `@tool`.
- **Secrets** (`ANTHROPIC_API_KEY`, etc.) always via environment variables /
  `.env`. Never hardcode or commit keys. `.env` is in `.gitignore`.
- **Commits** small and descriptive; every significant milestone is a candidate
  for a LinkedIn post (see `docs/`).

## Reference docs

- `docs/data-sources.md` — source catalog and which tool exploits each.
- `docs/report-structure.md` — what sections a GM/coach needs.

## What we do NOT want

- Rigid linear pipelines disguised as an agent.
- Reinventing what LangGraph already provides (memory, routing, checkpoints).
- Exposing API keys in the frontend or in the repo (it is public).

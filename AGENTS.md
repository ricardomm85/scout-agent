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

We build it **in public**: every milestone is written up in the devlog (see
"Devlog" below) and on LinkedIn. Documentation clarity is a goal, not an extra.

## Current status

**Day 3.** Two ReAct agents are working, both streamed step-by-step:

- **Hello-world agent** (`agent.py` + `tools.py`): one mock `injury_tool`. The
  point is the *decision* — the LLM chooses on its own to call the tool, reads
  the result, then answers. No fixed call sequence in code.
- **Text-to-SQL agent** (`sql_agent.py` + `sql_tools.py` + `db.py`): pointed at
  a database it has never seen, the agent lists the tables, reads the schema,
  writes its own `SELECT` (including a `JOIN` it derived from a foreign key),
  and answers in plain English. Backed by a toy SQLite DB (`scout.db`).

Next planned step: give the agent **both** capability families at once (the SQL
tools and the injury/news tool) and make it choose which one a question needs —
the dynamic routing that makes this an agent and not a pipeline.

The end product (scrapers for stats/injuries/contracts/YouTube, a FastAPI
endpoint, SSE streaming, Docker + Kamal deploy) is still ahead; see "Target
architecture".

## Repository layout

```
agent.py            # hello-world ReAct agent (Day 2): injury tool + streamed loop
tools.py            # mock injury tool — pure function, then @tool-wrapped
sql_agent.py        # text-to-SQL ReAct agent (Day 3): schema discovery + SELECT
sql_tools.py        # @tool wrappers over db.py (list_tables, describe_tables, run_sql)
db.py               # custom read-only SQLAlchemy data-access layer (see Conventions)
seed_db.py          # (re)builds the toy scout.db — idempotent
db_smoke_test.py    # smoke test for the DB layer (no agent)
smoke_test.py       # smoke test: can we reach the LLM and get a reply?
scout.db            # toy SQLite DB — gitignored, rebuild with seed_db.py
site/               # Astro build-in-public devlog, deployed to GitHub Pages
.github/workflows/deploy.yml   # deploys site/ to GitHub Pages
.env / .env.example # secrets + model id (.env is gitignored)
requirements.txt    # pinned direct deps
```

## Running the code

Everything runs from the project root with the venv active (or use
`.venv/bin/python <script>`):

```bash
python seed_db.py        # (re)build the toy database
python smoke_test.py     # confirm LLM reachability (no agent)
python tools.py          # test the pure injury function in isolation
python agent.py          # run the hello-world ReAct agent
python db_smoke_test.py  # test the DB layer in isolation
python sql_agent.py      # run the text-to-SQL ReAct agent
```

Tools and the DB layer are pure, testable functions — always runnable without
the agent. That is a hard convention, not a nicety (see below).

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
- **Agent framework:** LangGraph + LangChain 1.x. Agents are built with
  `langchain.agents.create_agent`, which wires the Reason → Act → Observe loop
  (binds tools, runs the model, executes tool calls, feeds results back, repeats
  until the model answers without a tool).
- **LLM — provider-agnostic by design.** The model is **one swappable line**;
  everything built on top (agents, tools) is provider-independent. Today it is
  **Google Gemini** via `langchain-google-genai` (`GOOGLE_API_KEY`,
  `GEMINI_MODEL`). Claude/Anthropic remains an equal candidate. **Never
  hardcode a model id** — it lives in the environment only. Do NOT copy model
  ids from old internet examples; verify the current id against the provider
  before setting it.
- **Database:** SQLAlchemy 2.x behind our own read-only layer (`db.py`). SQLite
  (`sqlite:///scout.db`) for the toy DB now; MySQL
  (`mysql+pymysql://readonly_user:***@host/scoutbasketball`) in production —
  only the connection URI changes. `pandas` for stat tables later.
- **Scraping (planned):** `httpx`/`requests`, BeautifulSoup, Playwright (for JS
  and light paywalled press).
- **API (planned):** FastAPI + uvicorn. Endpoint `POST /api/generate-report`.
- **Real time (planned):** SSE (Server-Sent Events) to stream the agent's
  "thinking" to the frontend (reports take 15–30s). Celery/Redis if a background
  task queue is needed.
- **Deployment (planned):** Docker + **Kamal** (push from local/CI over SSH to a
  VPS). Traefik as reverse proxy + Let's Encrypt.

## Conventions

- **Write the minimum that works.** Question whether code needs to exist (YAGNI),
  prefer stdlib and native platform/framework features over new dependencies, one
  line over fifty. Never simplify away validation at trust boundaries, error
  handling, security, or accessibility. The project conventions below always win
  over brevity.
- **Language:** everything in English — code, comments, and docs. Tool docstrings
  are CRITICAL: they are what the LLM reads to decide when to invoke each tool,
  so write them for the model (name, args, when to call, what it returns).
- **Tools = pure, testable functions.** Each function must run and be testable in
  isolation, without the agent. Write the pure function first, then wrap it with
  `@tool` (see `tools.py`, `sql_tools.py`).
- **The DB layer is ours, intentionally.** `langchain-community`'s `SQLDatabase`
  was archived (May 2026, no maintenance/security patches, no replacement), so
  we wrote a ~40-line read-only wrapper over SQLAlchemy (`db.py`). It exposes
  exactly three capabilities — list tables, read the schema, run a `SELECT` —
  and nothing else. **Do not reintroduce the archived helper.** Read-only is
  enforced in code, not in comments: `run_query` rejects anything that is not a
  single `SELECT`/`WITH`. Production must *also* use a read-only DB user
  (defense in depth), and remember this repo is public while the real data is
  not.
- **Secrets** (`GOOGLE_API_KEY`, future `ANTHROPIC_API_KEY`, DB credentials, etc.)
  always via environment variables / `.env`. Never hardcode or commit keys.
  `.env` is in `.gitignore`; `.env.example` is the template.
- **Commits** small and descriptive; every significant milestone is a devlog
  post and a candidate for LinkedIn.

## Devlog (build in public)

The old placeholder `docs/` files were removed. The build-in-public devlog now
lives in **`site/src/content/blog/`** (Astro) and is deployed to GitHub Pages by
`.github/workflows/deploy.yml`. Each milestone gets a numbered folder:
`01-…`, `02-…`, `03-…`. Read the latest post to see where the project actually
is before planning the next step.

`docs/report-structure.md` (what sections a GM/coach needs) is a **future** design
artifact — it does not exist yet.

## What we do NOT want

- Rigid linear pipelines disguised as an agent.
- Reinventing what LangGraph/LangChain already provides (memory, routing,
  checkpoints, the agent loop).
- Hardcoding LLM provider or model ids in code — keep the provider swappable.
- Reintroducing `langchain-community`'s archived `SQLDatabase`; the agent only
  ever gets our three read-only capabilities.
- Exposing API keys in the frontend or in the repo (it is public).

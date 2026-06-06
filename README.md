# 🏀 scout-agent

> An **AI agent system** that researches basketball players from real sources and
> writes scouting reports for coaches and sporting directors.

It is not a chatbot answering from memory. It is a **ReAct agent** (Reason +
Act): it reasons about what it needs to know, uses tools to research it (stats,
injuries, contracts, video), cross-checks the data, and writes an up-to-date
report.

I build it **in public**, step by step. Follow the process on
[LinkedIn](https://www.linkedin.com/in/ricardo-full-stack/).

## The idea

You give it a player:

```
Luka Doncic — PG/SG — Slovenia — 2.03m / 104kg — Last team: LA Lakers
```

And the agent, autonomously:

1. **Researches** advanced stats, contract situation, and agency.
2. **Flags risks** by scanning local press and X/Twitter for injuries.
3. **Analyzes tactics** by summarizing YouTube transcripts.
4. **Writes** a structured report for the decision-maker.

## Status

🚧 **Day 0** — laying the foundations. Next milestone: the agent "Hello World"
(an LLM that decides on its own to use a tool).

## Stack

`Python 3.13` · `LangGraph` · `Claude (Anthropic)` · `FastAPI` · `Playwright` ·
`Docker` · `Kamal`

---

_A [Scoutbasketball](https://scoutbasketball.com) project by
[Ricardo](https://www.linkedin.com/in/ricardo-full-stack/)._

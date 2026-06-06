---
title: "Day 2: the smallest agent that decides for itself"
description: "My Day 1 tracker couldn't make a single judgment call. So I built the smallest thing that can: a model that decides, by itself, to use a tool."
date: 2026-06-07
---

Day 1 ended with a verdict: I'd built a pipeline, and a pipeline can't make a
judgment call. It just shuttles text from one step to the next. That's how one
broken leg ended up in my report seven times.

So this time I built the opposite. The smallest thing that actually decides
something. No scraping, no report yet, just the part I got wrong last time, on its
own, where I could watch it.

## One model, one fake tool

The agent is a loop: the model thinks about what it's missing, maybe calls a tool,
reads what comes back, and keeps going until it can answer. Mine is the LLM, a
fake `get_injury_history(player)` that returns a few hardcoded lines, and the loop
itself, which the framework gives you.

Then I asked it one thing. The whole point: I never touched the tool myself.

```
Human:  Is Luka Doncic available to play right now?
AI   →  (calls get_injury_history with player_name="Luka Doncic")
Tool →  Left tibia fracture, surgery booked, ~3 months out, season over.
AI   →  No. He fractured his tibia and is out for the season.
```

That second line got me. The model worked out for itself that it needed the tool,
dug "Luka Doncic" out of my sentence, ran it, and answered from what came back. My
Day 1 code never had a moment like that. This whole thing is built around it.

## The bit I didn't expect

A tool's description isn't a comment for me. It's what the model reads to decide.
It never sees inside the function, just the name, the argument types, and the
docstring. Write something vague and it doesn't call the tool, or calls it wrong.
I spent more time on that one sentence than on the code under it.

## Cheap models, one catch

I'm building this on a free model to avoid burning money while I learn, and that's
fine, but with a catch I almost missed. An agent is useless if the model can't do
tool calling, and plenty of the cheap ones can't, or do it badly. So the question
isn't "is it free", it's "is it free *and* does it actually call tools". Pick
wrong and the agent just never reaches for anything.

## Next

One tool doesn't prove much. I want to see the model actually choosing: two tools,
a question where it has to pick the right one or use both, and let it sort that
out. That's next.

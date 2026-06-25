---
title: "Day 4: the agent chooses its own tools"
description: "Two agents became one. I gave it the injury tool and the stats database together and asked questions that force a choice. On the mixed question it grabbed both tools at once, before either had answered."
date: 2026-06-25
---

Days 2 and 3 both ended with the same promise: put both tools in the same room
and make the agent choose. This is that post.

## One agent, two ways of knowing

Until now I had two agents that each knew how to do one thing. One had a fake
injury lookup. One had a SQL database. Each only had one tool, so each only had
one move. That isn't choosing. That's a parlor trick with one card.

So I merged them. Four tools in one agent: the injury lookup, plus the three SQL
tools (list tables, read the schema, run a query). One system prompt.

## The call I had to make

Here's the thing I argued with myself over. How much do I tell it?

My SQL agent prescribes the order. List the tables, then describe them, then
write the query. One, two, three. That's fine when there's a single path and you
just want the model to walk it. Here there are two paths, and the whole point of
this post is which one it picks. If I prescribe the route, I've built a pipeline
wearing an agent costume.

So I didn't. The prompt names the two families and what each is for, then gets
out of the way. No "do this then that." The choice is the feature. Prescribe it
and you've deleted the feature.

## Three questions, three answers

I asked it three things, each engineered to force a different decision. Then I
watched which tools it reached for.

A stats question. It walked the SQL path and never touched the injury tool.

```
Human: How many points per game does Luka average (2025-26)?
AI  → list_tables()                          → players, stats
AI  → describe_tables("players, stats")      → (schema, with the foreign key)
AI  → run_sql("SELECT points … JOIN … WHERE name='Luka Doncic' AND season='2025-26'")
Tool → 29.4
AI  → 29.4 points per game.
```

An availability question. It went straight to the injury tool and never opened
the database.

```
Human: Is Luka available to play right now?
AI  → get_injury_history("Luka Doncic")
Tool → Left tibia fracture, surgery booked, ~3 months out, season over.
AI  → No. Serious left tibia fracture, ruled out for the season.
```

A mixed question. This is the one I cared about.

```
Human: Quick read on Luka: how he's performing, and is he available?
AI  → get_injury_history("Luka Doncic")   ┐
       list_tables()                       ┘  both, in the SAME step,
                                               before either had answered
Tool → players, stats
AI  → describe_tables("players, stats")  → run_sql("…season='2025-26'")
Tool → (29.4, 8.9, 8.1)
AI  → Unavailable: tibia fracture, out for the season.
      Before the injury: 29.4 pts / 8.9 reb / 8.1 ast per game.
```

## The bit that got me

That first step of the mixed question. The model read a sentence with two halves
and, before a single tool had returned anything, reached for both families at
once. In parallel. In the same step. It decided the question needed the database
and the injury lookup, and it wasn't going to do them one after the other when
it could do them together.

I didn't code that. There's no `if question_has_two_parts` in my source. I gave
it tools and stayed quiet, and it sorted the routing on its own. This is the
thing I've been promising since Day 2.

## A confession

The injury data is still the same four fake lines from Day 2. What's real here is
the pattern, not the numbers. Can the agent meet a question, pick the right tool
or tools, and stitch the answers together? It can. Swapping the mock for a real
scraper is a function-body change later. The routing above doesn't care where the
data came from.

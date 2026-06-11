---
title: "Day 3: the agent writes its own SQL"
description: "I pointed the agent at a database without telling it what was inside. It looked around, figured out the schema, and wrote the JOIN by itself."
date: 2026-06-11
---

Day 2 ended with a plan: give the agent two tools and watch it choose. I went a
different way. I gave it something real to chew on instead, a database, and the
more interesting thing happened on its own. It wrote its own SQL.

I didn't tell it the tables. I didn't tell it the columns. I gave it three small
tools (list the tables, describe a table, run a query) and one question in plain
English.

## Watching it figure things out

```
Human: How many points does Luka average this season (2025-26)?
AI  → list_tables()         → players, stats
AI  → describe_tables(...)  → (the schema, including a foreign key)
AI  → run_sql("SELECT points FROM stats JOIN players
               ON stats.player_id = players.id
               WHERE players.name = 'Luka Doncic' AND season = '2025-26'")
Tool → 29.4
AI  → Luka is averaging 29.4 points per game this season.
```

The JOIN got me. Nobody wrote that query. It saw the foreign key in the schema,
worked out that points live in one table and names in another, and stitched them
together. It even matched the season format, `2025-26` and not `2025`, because it
had glanced at a few example rows first. None of that is in my code. My code just
handed it the tools and got out of the way.

## The detour I didn't plan

I reached for the obvious helper to talk to the database, the one every tutorial
uses. Turns out it was archived two weeks ago. Done. No more fixes, no security
patches, and no drop-in replacement on the way.

So I wrote my own instead. About forty lines over SQLAlchemy, the library that
thing was wrapping anyway. Annoying for an afternoon, better in the end, because
now I decide what the agent can do, not a black box. And "read-only" stopped being
a hope in a comment and became a line of code: the query tool rejects anything
that isn't a SELECT. The model can ask for whatever it wants; it isn't writing to
my database.

That mattered more once I remembered this repo is public and the real data isn't.
The less the agent is trusted by default, the less there is to leak.

## A confession

The database here is fake. Four players, a handful of rows, made up. The point
wasn't the data, it was the pattern: can the agent meet a schema it's never seen
and find its way around? It can. Pointing it at a real database is a connection
string and a careful read-only user, not a rewrite.

## Next

Now it has two very different ways to learn about a player: a stats database it can
query, and the injury tool from Day 2. Time to put them in the same room and make
it choose which one the question actually needs. That's the part I keep promising.

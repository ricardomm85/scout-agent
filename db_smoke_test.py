"""Smoke test for the toy database — no agent involved yet.

Goal: confirm our own `Database` layer can connect to scout.db and expose it
the same way a SQL agent will read it: which tables exist, the schema with
sample rows, and that SELECTs run (and non-SELECTs are rejected).

Run it with:

    .venv/bin/python db_smoke_test.py
"""

from db import Database

# Same connection string we'll give the agent. For MySQL later this becomes
# "mysql+pymysql://user:pass@host/db" and nothing else changes.
db = Database("sqlite:///scout.db")

print("Tables the agent can see:", db.list_tables())

print("\n--- Schema + sample rows (this is what the agent reads) ---\n")
print(db.get_schema())

print("\n--- A SELECT, to prove read queries run ---")
print(
    db.run_query(
        "SELECT p.name, s.season, s.points "
        "FROM stats s JOIN players p ON p.id = s.player_id "
        "WHERE p.name = 'Luka Doncic' ORDER BY s.season"
    )
)

print("\n--- A write attempt, to prove it's blocked ---")
try:
    db.run_query("DROP TABLE players")
    print("ERROR: the write was NOT blocked!")
except ValueError as e:
    print("Blocked, as expected:", e)

"""Create and seed a toy SQLite database for the text-to-SQL experiment.

This is NOT the real scoutbasketball.com data — it's a tiny fake dataset
(a handful of players and their season stats) so we can learn how a SQL
agent introspects a schema and writes its own SELECT queries, without
touching the production MySQL database.

Run it directly to (re)build the database file:

    python seed_db.py

It is idempotent: it drops and recreates the tables every time, so you
always end up with the same clean state.
"""

import sqlite3

DB_PATH = "scout.db"

# Two related tables: a player, and many stat rows per player (one per season).
# Keeping it small on purpose — the point is the agent's reasoning, not the data.
SCHEMA = """
DROP TABLE IF EXISTS stats;
DROP TABLE IF EXISTS players;

CREATE TABLE players (
    id       INTEGER PRIMARY KEY,
    name     TEXT NOT NULL,
    team     TEXT NOT NULL,
    position TEXT NOT NULL
);

CREATE TABLE stats (
    id         INTEGER PRIMARY KEY,
    player_id  INTEGER NOT NULL,
    season     TEXT NOT NULL,
    points     REAL NOT NULL,   -- points per game
    rebounds   REAL NOT NULL,   -- rebounds per game
    assists    REAL NOT NULL,   -- assists per game
    FOREIGN KEY (player_id) REFERENCES players(id)
);
"""

# (name, team, position)
PLAYERS = [
    (1, "Luka Doncic",        "Los Angeles Lakers",  "Guard"),
    (2, "Nikola Jokic",       "Denver Nuggets",      "Center"),
    (3, "Victor Wembanyama",  "San Antonio Spurs",   "Center"),
    (4, "Santi Aldama",       "Memphis Grizzlies",   "Forward"),
]

# (player_id, season, points, rebounds, assists)
STATS = [
    (1, "2024-25", 28.1, 8.3, 7.8),
    (1, "2025-26", 29.4, 8.9, 8.1),
    (2, "2024-25", 26.4, 12.7, 9.0),
    (2, "2025-26", 27.1, 12.1, 9.8),
    (3, "2024-25", 21.4, 10.6, 3.7),
    (3, "2025-26", 24.3, 11.2, 4.1),
    (4, "2025-26", 12.8, 6.4, 2.5),
]


def main() -> None:
    # `with` commits on success and closes the connection for us.
    with sqlite3.connect(DB_PATH) as conn:
        conn.executescript(SCHEMA)
        conn.executemany(
            "INSERT INTO players (id, name, team, position) VALUES (?, ?, ?, ?)",
            PLAYERS,
        )
        conn.executemany(
            "INSERT INTO stats (player_id, season, points, rebounds, assists) "
            "VALUES (?, ?, ?, ?, ?)",
            STATS,
        )

    print(f"Built {DB_PATH}: {len(PLAYERS)} players, {len(STATS)} stat rows.")


if __name__ == "__main__":
    main()

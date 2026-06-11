"""Thin, read-only data-access layer over SQLAlchemy.

This replaces langchain-community's `SQLDatabase`, which was archived in
May 2026 (no more maintenance or security patches). It gives the agent
exactly three capabilities — list tables, read the schema, run a SELECT —
and nothing else, so *we* decide precisely what the LLM is allowed to touch.

Same code works for SQLite (the toy db) and MySQL (production): only the
connection URI changes.

    sqlite:///scout.db
    mysql+pymysql://readonly_user:***@host/scoutbasketball
"""

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.schema import CreateTable, MetaData

# How many example rows to show per table when describing the schema. Seeing
# real values (e.g. season is "2024-25", not 2024) helps the LLM write correct
# queries — the same trick langchain-community used.
SAMPLE_ROWS = 3


class Database:
    """A minimal, read-only window onto a SQL database."""

    def __init__(self, uri: str):
        self.engine = create_engine(uri)

    def list_tables(self) -> list[str]:
        """Return the names of the tables the agent is allowed to see."""
        return inspect(self.engine).get_table_names()

    def get_schema(self, tables: list[str] | None = None) -> str:
        """Return CREATE TABLE statements plus a few sample rows per table.

        This is the text the agent reads to understand the database before
        writing any query. If `tables` is None, describe them all.
        """
        names = tables or self.list_tables()

        # Reflection: SQLAlchemy reads the live database and rebuilds the table
        # definitions (columns, types, primary/foreign keys) as Python objects.
        metadata = MetaData()
        metadata.reflect(bind=self.engine, only=names)

        blocks = []
        for name in names:
            table = metadata.tables[name]
            # CreateTable renders a real CREATE statement in this database's
            # dialect — including the FOREIGN KEYs, so the LLM learns how to JOIN.
            ddl = str(CreateTable(table).compile(dialect=self.engine.dialect)).strip()
            blocks.append(f"{ddl}\n\n{self._sample_rows(name)}")

        return "\n\n".join(blocks)

    def run_query(self, sql: str) -> list[tuple]:
        """Execute a single read-only SELECT and return the rows.

        Defense in depth: even though production should also use a read-only
        database user, we reject anything that isn't a single SELECT here, so
        the agent can never write, drop, or chain a second statement.
        """
        cleaned = sql.strip().rstrip(";").strip()
        lowered = cleaned.lower()
        if not (lowered.startswith("select") or lowered.startswith("with")):
            raise ValueError("Only read-only SELECT queries are allowed.")
        if ";" in cleaned:
            raise ValueError("Only a single statement is allowed.")

        with self.engine.connect() as conn:
            result = conn.execute(text(cleaned))
            return [tuple(row) for row in result]

    def _sample_rows(self, table: str) -> str:
        """A few example rows from `table`, formatted as a readable comment."""
        # `table` comes from our own inspector (never user input), so
        # interpolating the name here is safe.
        with self.engine.connect() as conn:
            result = conn.execute(text(f"SELECT * FROM {table} LIMIT {SAMPLE_ROWS}"))
            columns = list(result.keys())
            rows = [tuple(row) for row in result]

        lines = ["\t".join(columns)]
        lines += ["\t".join(str(value) for value in row) for row in rows]
        body = "\n".join(lines)
        return f"/*\n{len(rows)} rows from {table} table:\n{body}\n*/"

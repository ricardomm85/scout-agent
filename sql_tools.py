"""SQL tools for the agent — thin @tool wrappers over db.py.

Following the project convention: the real logic lives in db.py as plain,
testable functions; here we only wrap it so the LLM can call it. The
docstrings ARE the interface the model reads to decide which tool to use
and in what order, so they're written for the model, not for humans.

The three tools mirror how a careful analyst works against an unknown
database: first see what tables exist, then read their schema, then —
and only then — write a query.
"""

from langchain_core.tools import tool

from db import Database

# One shared read-only connection for all the tools. Swap this URI for the
# MySQL one in production; nothing else here changes.
db = Database("sqlite:///scout.db")


@tool
def list_tables() -> str:
    """List the names of all tables available in the database.

    Call this FIRST, before anything else, to discover what data exists.
    You cannot know the table names in advance — always start here.
    """
    return ", ".join(db.list_tables())


@tool
def describe_tables(tables: str) -> str:
    """Show the schema (columns, types, keys) and a few sample rows for tables.

    Call this AFTER list_tables, for the tables that look relevant, to learn
    their columns and how they relate (foreign keys) before writing any query.

    Args:
        tables: Comma-separated table names, e.g. "players, stats".

    Returns:
        The CREATE TABLE statements plus example rows for those tables.
    """
    names = [t.strip() for t in tables.split(",") if t.strip()]
    return db.get_schema(names)


@tool
def run_sql(query: str) -> str:
    """Run a single read-only SQL SELECT query and return the resulting rows.

    Call this LAST, once you know the schema, to fetch the answer. Only SELECT
    queries are allowed — writes are rejected. If the query errors, read the
    error, fix the SQL, and try again.

    Args:
        query: One SQL SELECT statement, in SQLite dialect.

    Returns:
        The result rows as text, or an error message if the query is invalid.
    """
    try:
        rows = db.run_query(query)
    except Exception as e:
        # Hand the error back to the model so it can self-correct on the next step.
        return f"Query failed: {e}"
    return str(rows)

"""Mock tools for the scout-agent hello world.

These return FAKE, hardcoded data on purpose. The goal right now is not real
data — it's to give the agent something it can *decide* to call. A real scraper
replaces the function body later; the signature, docstring and @tool wrapper
stay the same.

Convention (see CLAUDE.md): write a pure, testable function FIRST, then wrap it
as a tool. That way the function runs and is testable in isolation, no agent.
"""

from langchain_core.tools import tool


def get_injury_history(player_name: str) -> str:
    """Look up a basketball player's recent injury history.

    Use this whenever you need to know if a player is currently injured, what
    happened, how serious it is, or when they are expected to return. Call it
    before writing anything about a player's availability or fitness.

    Args:
        player_name: Full name of the player, e.g. "Luka Doncic".

    Returns:
        A short plain-text injury report (dates, diagnosis, severity, expected
        return), or a "no data found" message if the player is unknown.
    """
    # FAKE data — a real scraper replaces this body later. Keyed by a lowercase
    # name so "Luka Doncic" and "luka doncic" both match.
    fake_db = {
        "luka doncic": (
            "Injury report for Luka Doncic:\n"
            "- 2026-05-28: Left tibia fracture suffered vs. Barcelona.\n"
            "- Severity: serious. Surgery scheduled for 2026-06-03.\n"
            "- Expected return: ~3 months. Ruled out for the rest of the season."
        ),
    }
    return fake_db.get(
        player_name.lower(),
        f"No injury data found for {player_name}.",
    )


# Wrap the pure function so the agent can use it. `tool(...)` reads the name,
# type hints and docstring above to build the schema the LLM sees.
injury_tool = tool(get_injury_history)


if __name__ == "__main__":
    # Test the PURE function alone — no agent. It's just a function, so call it
    # directly and eyeball the output before wiring it into the agent.
    print(get_injury_history("Luka Doncic"))
    print("---")
    print(get_injury_history("Some Unknown Player"))

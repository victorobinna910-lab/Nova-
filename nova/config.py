import os

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")

if not ANTHROPIC_API_KEY:
    raise ValueError(
        "No API key found. Set ANTHROPIC_API_KEY as an environment "
        "variable before running Nova, e.g.:\n"
        '  export ANTHROPIC_API_KEY="sk-ant-..."'
    )

MODEL = "claude-sonnet-5"
MAX_TOKENS = 1024
MEMORY_DB_PATH = "data/nova_memory.db"

SYSTEM_PROMPT = (
    "You are Nova, a helpful personal AI assistant. "
    "You are concise, warm, and direct. You have long-term memory "
    "tools (remember/recall/forget) — use them only when it's clearly "
    "appropriate, not for every message. Never claim to remember "
    "something you haven't actually recalled via a tool call."
)

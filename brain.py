from anthropic import Anthropic

from config import ANTHROPIC_API_KEY, MODEL, MAX_TOKENS, SYSTEM_PROMPT
from memory import NovaMemory


MEMORY_TOOLS = [
    {
        "name": "remember",
        "description": (
            "Save a fact for later, permanently, across conversations. "
            "Only call this when the user explicitly asks you to "
            "remember something, or clearly states a fact they want "
            "kept. Do not call this for casual chat."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "key": {"type": "string", "description": "Short label, e.g. 'wifi_password'"},
                "value": {"type": "string", "description": "The fact itself"},
            },
            "required": ["key", "value"],
        },
    },
    {
        "name": "recall",
        "description": (
            "Search Nova's long-term memory for anything relevant to "
            "the user's question. Call this when the user asks about "
            "something they may have told you to remember before."
        ),
        "input_schema": {
            "type": "object",
            "properties": {"query": {"type": "string", "description": "What to search for"}},
            "required": ["query"],
        },
    },
    {
        "name": "forget",
        "description": "Delete a previously remembered fact by its key.",
        "input_schema": {
            "type": "object",
            "properties": {"key": {"type": "string", "description": "The key to delete"}},
            "required": ["key"],
        },
    },
]


class NovaBrain:
    """Nova's reasoning engine with Claude-powered memory tools."""

    def __init__(self):
        self.client = Anthropic(api_key=ANTHROPIC_API_KEY)
        self.memory = NovaMemory()

    def _run_tool(self, tool_name: str, tool_input: dict) -> str:
        """Execute a memory tool and return its result for Claude."""
        if tool_name == "remember":
            self.memory.remember(tool_input["key"], tool_input["value"])
            return f"Saved: {tool_input['key']} = {tool_input['value']}"

        if tool_name == "recall":
            results = self.memory.search(tool_input["query"])
            if not results:
                return "No matching memories found."
            return "\n".join(f"{key}: {value}" for key, value in results)

        if tool_name == "forget":
            deleted = self.memory.forget(tool_input["key"])
            return "Deleted." if deleted else "Nothing found with that key."

        return f"Unknown tool: {tool_name}"

    def think(self, user_input: str, conversation_history: list | None = None) -> str:
        """Send input to Claude and return Nova's final text response."""
        messages = conversation_history[:] if conversation_history else []
        messages.append({"role": "user", "content": user_input})

        while True:
            response = self.client.messages.create(
                model=MODEL,
                max_tokens=MAX_TOKENS,
                system=SYSTEM_PROMPT,
                tools=MEMORY_TOOLS,
                messages=messages,
            )

            if response.stop_reason != "tool_use":
                return response.content[0].text

            messages.append({"role": "assistant", "content": response.content})
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    result_text = self._run_tool(block.name, block.input)
                    tool_results.append(
                        {
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": result_text,
                        }
                    )
            messages.append({"role": "user", "content": tool_results})

    def close(self) -> None:
        """Release the memory database connection."""
        self.memory.close()

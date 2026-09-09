"""Small JSON-backed conversation history for the Cred agent."""

import json
from pathlib import Path
from typing import Any


DEFAULT_MEMORY_PATH = Path(__file__).parent / "conversation_memory.json"


class ConversationMemory:
    """Persist and retrieve ordered user/assistant messages."""

    def __init__(self, path: Path = DEFAULT_MEMORY_PATH) -> None:
        self.path = Path(path)
        self.messages: list[dict[str, str]] = []
        self.load()

    def load(self) -> list[dict[str, str]]:
        if self.path.exists():
            self.messages = json.loads(self.path.read_text(encoding="utf-8"))
        return self.messages

    def add(self, role: str, content: str) -> None:
        if role not in {"user", "assistant"}:
            raise ValueError("role must be 'user' or 'assistant'")
        self.messages.append({"role": role, "content": content})
        self.path.write_text(json.dumps(self.messages, indent=2), encoding="utf-8")

    def reset(self) -> None:
        self.messages = []
        if self.path.exists():
            self.path.unlink()

    def context(self) -> list[dict[str, str]]:
        return list(self.messages)

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Any

@dataclass
class Memory:
    """A tiny short-term memory buffer for the agent."""
    messages: List[Dict[str, Any]] = field(default_factory=list)

    def add(self, role: str, content: str | None = None, tool_call_id: str | None = None, name: str | None = None):
        msg: Dict[str, Any] = {"role": role}
        if content is not None:
            msg["content"] = content
        if tool_call_id is not None:
            msg["tool_call_id"] = tool_call_id
        if name is not None:
            msg["name"] = name
        self.messages.append(msg)

    def as_list(self) -> List[Dict[str, Any]]:
        return self.messages

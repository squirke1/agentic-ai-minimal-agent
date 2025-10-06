"""Short-term memory management for the AI agent.

This module provides a simple buffer for maintaining conversation context
and message history during a single agent session.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Any

@dataclass
class Memory:
    """Short-term memory buffer for agent conversations.
    
    Maintains a list of messages in OpenAI chat format, storing the
    conversation history and tool interactions within a single session.
    
    Attributes:
        messages: List of message dictionaries in OpenAI format
    """
    messages: List[Dict[str, Any]] = field(default_factory=list)

    def add(self, role: str, content: str | None = None, tool_call_id: str | None = None, name: str | None = None):
        """Add a message to the conversation history.
        
        Args:
            role: Message role ('system', 'user', 'assistant', 'function')
            content: Message content (optional for function calls)
            tool_call_id: ID for tool call responses (optional)
            name: Name for function/tool messages (optional)
        """
        msg: Dict[str, Any] = {"role": role}
        if content is not None:
            msg["content"] = content
        if tool_call_id is not None:
            msg["tool_call_id"] = tool_call_id
        if name is not None:
            msg["name"] = name
        self.messages.append(msg)

    def as_list(self) -> List[Dict[str, Any]]:
        """Get messages as a list compatible with OpenAI API.
        
        Returns:
            List of message dictionaries
        """
        return self.messages

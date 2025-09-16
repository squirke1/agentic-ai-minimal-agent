"""
Memory management for the minimal agentic AI agent.
Provides simple in-memory storage for conversation history and context.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import json


class Memory:
    """
    Simple memory implementation for storing conversation history and context.
    """
    
    def __init__(self, limit: int = 100):
        """
        Initialize memory with a limit on the number of entries.
        
        Args:
            limit: Maximum number of memory entries to store
        """
        self.limit = limit
        self.entries: List[Dict[str, Any]] = []
        self.context: Dict[str, Any] = {}
    
    def add_entry(self, role: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Add a new entry to memory.
        
        Args:
            role: The role (user, assistant, system)
            content: The content of the message
            metadata: Optional metadata about the entry
        """
        entry = {
            "timestamp": datetime.now().isoformat(),
            "role": role,
            "content": content,
            "metadata": metadata or {}
        }
        
        self.entries.append(entry)
        
        # Keep only the most recent entries within the limit
        if len(self.entries) > self.limit:
            self.entries = self.entries[-self.limit:]
    
    def get_recent_entries(self, count: int = 10) -> List[Dict[str, Any]]:
        """
        Get the most recent entries from memory.
        
        Args:
            count: Number of recent entries to retrieve
            
        Returns:
            List of recent memory entries
        """
        return self.entries[-count:] if self.entries else []
    
    def get_conversation_history(self) -> List[Dict[str, str]]:
        """
        Get conversation history formatted for OpenAI API.
        
        Returns:
            List of messages formatted for OpenAI chat completion
        """
        return [
            {"role": entry["role"], "content": entry["content"]}
            for entry in self.entries
            if entry["role"] in ["user", "assistant", "system"]
        ]
    
    def set_context(self, key: str, value: Any) -> None:
        """
        Set a context variable.
        
        Args:
            key: Context key
            value: Context value
        """
        self.context[key] = value
    
    def get_context(self, key: str, default: Any = None) -> Any:
        """
        Get a context variable.
        
        Args:
            key: Context key
            default: Default value if key doesn't exist
            
        Returns:
            Context value or default
        """
        return self.context.get(key, default)
    
    def clear(self) -> None:
        """Clear all memory entries and context."""
        self.entries.clear()
        self.context.clear()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Export memory to dictionary.
        
        Returns:
            Dictionary representation of memory
        """
        return {
            "entries": self.entries,
            "context": self.context,
            "limit": self.limit
        }
    
    def from_dict(self, data: Dict[str, Any]) -> None:
        """
        Import memory from dictionary.
        
        Args:
            data: Dictionary containing memory data
        """
        self.entries = data.get("entries", [])
        self.context = data.get("context", {})
        self.limit = data.get("limit", 100)
    
    def save_to_file(self, filepath: str) -> None:
        """
        Save memory to JSON file.
        
        Args:
            filepath: Path to save the memory file
        """
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
    
    def load_from_file(self, filepath: str) -> None:
        """
        Load memory from JSON file.
        
        Args:
            filepath: Path to the memory file
        """
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
                self.from_dict(data)
        except FileNotFoundError:
            # File doesn't exist, start with empty memory
            pass
from __future__ import annotations
import math, os, json, glob
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

# ---- Tool registry ----

_TOOL_REGISTRY: Dict[str, "Tool"] = {}

@dataclass
class Tool:
    name: str
    description: str
    schema: Dict[str, Any]
    run: Any

    def to_openai_spec(self) -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.schema,
            },
        }

def register(tool: Tool):
    _TOOL_REGISTRY[tool.name] = tool


def all_openai_specs() -> List[Dict[str, Any]]:
    return [t.to_openai_spec() for t in _TOOL_REGISTRY.values()]


def call_tool(name: str, arguments_json: Any) -> str:
    if name not in _TOOL_REGISTRY:
        return json.dumps({"error": f"Unknown tool: {name}"})
    tool = _TOOL_REGISTRY[name]
    try:
        if isinstance(arguments_json, str):
            args = json.loads(arguments_json or "{}")
        elif arguments_json is None:
            args = {}
        else:
            args = arguments_json
        return tool.run(**args)
    except Exception as e:
        return json.dumps({"error": str(e)})

# ---- Global memory instance ----
_VECTOR_MEMORY = None

def get_vector_memory():
    """Get or create the global vector memory instance"""
    global _VECTOR_MEMORY
    if _VECTOR_MEMORY is None:
        try:
            from long_term_memory import VectorMemory, CHROMADB_AVAILABLE
            if CHROMADB_AVAILABLE:
                _VECTOR_MEMORY = VectorMemory()
            else:
                print("ChromaDB not available. Long-term memory disabled.")
                return None
        except ImportError as e:
            print(f"Long-term memory not available: {e}")
            return None
        except Exception as e:
            print(f"Error initializing long-term memory: {e}")
            return None
    return _VECTOR_MEMORY

# ---- Memory Management Tools ----

class StoreMemoryArgs(BaseModel):
    content: str = Field(..., description="The content to store in long-term memory")
    memory_type: str = Field("experience", description="Type: conversation, experience, fact, or skill")
    importance: float = Field(0.5, description="Importance score 0.0-1.0")

def _store_memory_run(content: str, memory_type: str = "experience", importance: float = 0.5) -> str:
    try:
        memory = get_vector_memory()
        if memory is None:
            return json.dumps({"error": "Long-term memory not available. Install: pip install chromadb sentence-transformers"})
        
        memory_id = memory.store_memory(content, memory_type, importance=importance)
        return json.dumps({
            "success": True,
            "memory_id": memory_id,
            "content": content[:100] + "..." if len(content) > 100 else content,
            "type": memory_type,
            "importance": importance
        })
    except Exception as e:
        return json.dumps({"error": str(e)})

register(Tool(
    name="store_memory",
    description="Store important information in long-term memory for future reference.",
    schema={
        "type": "object",
        "properties": {
            "content": {"type": "string", "description": "The content to store"},
            "memory_type": {"type": "string", "enum": ["conversation", "experience", "fact", "skill"], "default": "experience"},
            "importance": {"type": "number", "minimum": 0.0, "maximum": 1.0, "default": 0.5}
        },
        "required": ["content"],
    },
    run=_store_memory_run,
))

class SearchMemoryArgs(BaseModel):
    query: str = Field(..., description="What to search for in memory")
    memory_type: Optional[str] = Field(None, description="Optional: filter by memory type")
    n_results: int = Field(5, description="Number of results to return")

def _search_memory_run(query: str, memory_type: Optional[str] = None, n_results: int = 5) -> str:
    try:
        memory = get_vector_memory()
        if memory is None:
            return json.dumps({"error": "Long-term memory not available"})
        
        results = memory.search_memories(query, n_results, memory_type)
        
        formatted_results = []
        for result in results:
            formatted_results.append({
                "content": result["content"],
                "type": result["memory_type"],
                "similarity": round(result["similarity"], 3),
                "timestamp": result["timestamp"],
                "importance": result["importance"]
            })
        
        return json.dumps({
            "query": query,
            "found": len(formatted_results),
            "memories": formatted_results
        })
    except Exception as e:
        return json.dumps({"error": str(e)})

register(Tool(
    name="search_memory",
    description="Search long-term memory for relevant information using semantic similarity.",
    schema={
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "What to search for"},
            "memory_type": {"type": "string", "enum": ["conversation", "experience", "fact", "skill"]},
            "n_results": {"type": "integer", "minimum": 1, "maximum": 20, "default": 5}
        },
        "required": ["query"],
    },
    run=_search_memory_run,
))

class GetRecentMemoriesArgs(BaseModel):
    n_results: int = Field(10, description="Number of recent memories to retrieve")
    memory_type: Optional[str] = Field(None, description="Optional: filter by memory type")

def _get_recent_memories_run(n_results: int = 10, memory_type: Optional[str] = None) -> str:
    try:
        memory = get_vector_memory()
        if memory is None:
            return json.dumps({"error": "Long-term memory not available"})
        
        results = memory.get_recent_memories(n_results, memory_type)
        
        formatted_results = []
        for result in results:
            formatted_results.append({
                "content": result["content"],
                "type": result["memory_type"],
                "timestamp": result["timestamp"],
                "importance": result["importance"]
            })
        
        return json.dumps({
            "count": len(formatted_results),
            "memories": formatted_results
        })
    except Exception as e:
        return json.dumps({"error": str(e)})

register(Tool(
    name="get_recent_memories",
    description="Get the most recently stored memories.",
    schema={
        "type": "object",
        "properties": {
            "n_results": {"type": "integer", "minimum": 1, "maximum": 50, "default": 10},
            "memory_type": {"type": "string", "enum": ["conversation", "experience", "fact", "skill"]}
        },
        "required": [],
    },
    run=_get_recent_memories_run,
))

def _memory_stats_run() -> str:
    try:
        memory = get_vector_memory()
        if memory is None:
            return json.dumps({"error": "Long-term memory not available"})
        
        stats = memory.get_memory_stats()
        return json.dumps(stats)
    except Exception as e:
        return json.dumps({"error": str(e)})

register(Tool(
    name="memory_stats",
    description="Get statistics about the long-term memory database.",
    schema={
        "type": "object",
        "properties": {},
        "required": [],
    },
    run=_memory_stats_run,
))

# ---- Calculator ----

class CalcArgs(BaseModel):
    expression: str = Field(..., description="A math expression, e.g. '2*(3+4)'.")


def _calc_run(expression: str) -> str:
    try:
        # safe eval using math namespace only
        allowed = {k: getattr(math, k) for k in dir(math) if not k.startswith("_")}
        allowed.update({"__builtins__": {}})
        result = eval(expression, allowed, {})
        return json.dumps({"ok": True, "expression": expression, "result": result})
    except Exception as e:
        return json.dumps({"ok": False, "error": str(e)})

register(Tool(
    name="calculator",
    description="Evaluate a mathematical expression using Python math.",
    schema={
        "type": "object",
        "properties": {
            "expression": {"type": "string", "description": "Math expression, e.g. '2*(3+4)'."}
        },
        "required": ["expression"],
    },
    run=_calc_run,
))

# ---- Retrieve (RAG-lite over ./docs) ----

class RetrieveArgs(BaseModel):
    query: str = Field(..., description="What to search for in local docs.")
    k: int = Field(3, description="How many chunks to return.")


def _retrieve_run(query: str, k: int = 3) -> str:
    # naive full-text search over ./docs/*.md
    docs = []
    for path in glob.glob("docs/*.md"):
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
            docs.append((path, text))
    query_l = query.lower()
    scored = []
    for path, text in docs:
        score = text.lower().count(query_l)
        if score:
            scored.append((score, path, text))
    scored.sort(reverse=True)
    results = []
    for _, path, text in scored[:k]:
        snippet = text[:800]
        results.append({"path": path, "snippet": snippet})
    return json.dumps({"query": query, "hits": results})

register(Tool(
    name="retrieve",
    description="Search local Markdown files in ./docs and return snippets.",
    schema={
        "type": "object",
        "properties": {
            "query": {"type": "string"},
            "k": {"type": "integer", "default": 3}
        },
        "required": ["query"],
    },
    run=_retrieve_run,
))

# ---- Web search (stub) ----

class WebArgs(BaseModel):
    query: str = Field(..., description="Web search query.")


def _web_search_run(query: str) -> str:
    # Stub that returns a static response; replace with a real API as needed.
    return json.dumps({
        "query": query,
        "results": [
            {"title": "How to integrate web search", "url": "https://example.com/search-guide", "snippet": "Replace the stub with your API."}
        ]
    })

register(Tool(
    name="web_search",
    description="Search the web (stub; wire to your provider).",
    schema={
        "type": "object",
        "properties": {"query": {"type": "string"}},
        "required": ["query"],
    },
    run=_web_search_run,
))

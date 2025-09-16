from __future__ import annotations
import math, os, json, glob
from dataclasses import dataclass
from typing import Any, Dict, List
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


def call_tool(name: str, arguments_json: str) -> str:
    if name not in _TOOL_REGISTRY:
        return json.dumps({"error": f"Unknown tool: {name}"})
    tool = _TOOL_REGISTRY[name]
    try:
        args = json.loads(arguments_json or "{}")
        return tool.run(**args)
    except Exception as e:
        return json.dumps({"error": str(e)})

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

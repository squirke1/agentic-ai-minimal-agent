# Agentic AI — Minimal Agent

A tiny reference implementation of an "agent" powered by an LLM with
- function/tool calling
- a planner–executor loop with a step limit
- a simple memory buffer
- file-based retrieval (RAG-lite)

## Quickstart

### 1) Python & deps
- Python 3.10+
- `pip install -r requirements.txt`

### 2) Configure
Copy `.env.example` to `.env` and set your keys:
```bash
cp .env.example .env
```

# Agentic AI — Minimal Agent

A minimal reference implementation of an AI agent with the following capabilities:
- Function/tool calling
- Planner-executor loop with step limits
- Short and long-term memory
- Vector-based memory with semantic search
- Document retrieval (RAG)

## Getting Started

### Setup
- Python 3.9+
- Install dependencies: `pip install -r requirements.txt`

### Configuration
Copy `.env.example` to `.env` and add your OpenAI API key:
```bash
cp .env.example .env
```

### Running the Agent

```bash
python main.py --task "Calculate compound interest for $1000 at 5% for 10 years"
```

For testing without API calls:
```bash
python test_agent.py    # Test components
python demo_agent.py    # Full demo workflow
```

### Adding Documents
Place Markdown files in `./docs/` for the agent to search and reference.

## Architecture

The agent follows a planner-executor pattern where the LLM decides which tools to call and the runtime executes them. Available tools include calculator, document retrieval, memory management, and web search.

Memory operates at two levels:
- **Short-term**: Conversation context within a session
- **Long-term**: Persistent vector storage across sessions using ChromaDB

## Memory System

The agent maintains different types of memories:
- Experience: Task results and learned patterns
- Fact: Important information
- Skill: Acquired capabilities
- Conversation: Notable exchanges

Memory operations include storing new information, searching for relevant past experiences, and retrieving recent memories. The system uses vector embeddings for semantic similarity matching.

## Safety Features

- Step limit (default 6) prevents infinite loops
- Input validation using Pydantic
- Memory importance scoring
- Error handling and recovery

## Configuration

Set the `MODEL` environment variable to use different OpenAI-compatible models. The system requires function calling support.

## Extensions

Some potential improvements:
- Connect web_search to a real API (SerpAPI, Tavily, etc.)
- Add task decomposition capabilities
- Implement logging and observability
- Add input/output validation and guardrails

## License

MIT

## Architecture

The agent follows a planner-executor pattern where the LLM decides which tools to call and the runtime executes them. Available tools include calculator, document retrieval, memory management, and web search.

Memory operates at two levels:
- **Short-term**: Conversation context within a session
- **Long-term**: Persistent vector storage across sessions using ChromaDB

## Memory System

The agent maintains different types of memories:
- Experience: Task results and learned patterns
- Fact: Important information
- Skill: Acquired capabilities
- Conversation: Notable exchanges

Memory operations include storing new information, searching for relevant past experiences, and retrieving recent memories. The system uses vector embeddings for semantic similarity matching.

## Safety Features

- Step limit (default 6) prevents infinite loops
- Input validation using Pydantic
- Memory importance scoring
- Error handling and recovery

## Configuration

Set the `MODEL` environment variable to use different OpenAI-compatible models. The system requires function calling support.

## Extensions

Some potential improvements:
- Connect web_search to a real API (SerpAPI, Tavily, etc.)
- Add task decomposition capabilities
- Implement logging and observability
- Add input/output validation and guardrails

## License

MIT

## License

MIT

---

## How to publish as a repo

1. Create a new GitHub repository, e.g. `agentic-ai-minimal-agent`.
2. Add the files above.
3. Commit & push.
4. (Optional) Add a short demo GIF of running `main.py`.

---

## Suggested README Badges

* Python 3.10+
* MIT License
* Works with OpenAI-compatible APIs

---

## Next Steps / Extensions

* Wire `web_search` to a real provider (SerpAPI, Tavily, Bing, etc.).
* Add a **task decomposition** tool (e.g., `make_plan`) to externalize planning.
* Persist **long-term memory** to a vector DB (FAISS, Chroma) for multi-session continuity.
* Add **observability**: log steps, tool calls, and token usage.
* Implement **guardrails** (input/output validation, allowlist tools only).
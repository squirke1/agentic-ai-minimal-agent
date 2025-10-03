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

A tiny reference implementation of an "agent" powered by an LLM with
- function/tool calling
- a planner–executor loop with a step limit
- a simple memory buffer
- **long-term vector memory with semantic search**
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

### 3) Run

```bash
python main.py --task "Plan a 2-hour study session on agentic AI using the docs and calculate the total minutes spent on each topic."
```

**Note**: You need a valid OpenAI API key and billing setup. If you get quota errors, you can test the system without API calls:

```bash
# Test all components without API calls
python test_agent.py

# See a complete demo workflow
python demo_agent.py
```

### 4) Optional: Add reference docs

Put Markdown files in `./docs`. The `retrieve` tool will chunk & search them.

## Design

* **Planner–executor**: the LLM decides when to call tools; the runtime executes and returns results.
* **Tools**: Calculator, Retrieve (RAG-lite over `./docs`), Memory Management, and a minimal Web Search stub you can wire to your preferred API.
* **Short-term Memory**: conversation + tool results are fed back to the LLM each step.
* **Long-term Memory**: persistent vector database stores experiences, facts, and learnings across sessions.

## New: Long-Term Memory Features

The agent now includes persistent memory capabilities:

### Memory Types
- **Experience**: Task results and learned patterns
- **Fact**: Important information to remember
- **Skill**: Acquired capabilities and techniques
- **Conversation**: Important dialogue exchanges

### Memory Tools
- `store_memory(content, type, importance)`: Save information for future use
- `search_memory(query, type, n_results)`: Find relevant past experiences
- `get_recent_memories(n_results, type)`: Get recent memories
- `memory_stats()`: View memory database statistics

### Automatic Memory Management
- Agent automatically searches for relevant past experiences before starting tasks
- Successful task completions are stored for future reference
- Failed attempts are logged with lower importance scores
- Vector similarity search finds semantically related memories

### Memory Database
- Uses ChromaDB for vector storage
- Sentence-transformers for embeddings
- Persistent storage in `./memory_db/`
- Semantic similarity search across all stored memories

## Safety & Limits

* Hard step cap (default 6) prevents infinite loops.
* Tool arguments validated with `pydantic`.
* Memory importance scoring prevents information overload.

## Swap-in Models

Set `MODEL` in `.env`. Tested with OpenAI-compatible chat completions that support tool/function calling.

### 4) Optional: Add reference docs

Put Markdown files in `./docs`. The `retrieve` tool will chunk & search them.

## Design

* **Planner–executor**: the LLM decides when to call tools; the runtime executes and returns results.
* **Tools**: Calculator, Retrieve (RAG-lite over `./docs`), and a minimal Web Search stub you can wire to your preferred API.
* **Memory**: conversation + tool results are fed back to the LLM each step.

## Safety & Limits

* Hard step cap (default 6) prevents infinite loops.
* Tool arguments validated with `pydantic`.

## Swap-in Models

Set `MODEL` in `.env`. Tested with OpenAI-compatible chat completions that support tool/function calling.

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
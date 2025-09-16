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

### 3) Run

```bash
python main.py --task "Plan a 2-hour study session on agentic AI using the docs and do a quick cost estimate with the calculator."
```

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
from __future__ import annotations
import argparse, json, os
from dotenv import load_dotenv
from openai import OpenAI
from memory import Memory
from tools import all_openai_specs, call_tool
from openai.types.chat import ChatCompletionMessageParam

SYSTEM_PROMPT = (
    "You are an autonomous but careful AI agent. "
    "Plan tasks, call tools when helpful, and finish with a concise, well-structured answer. "
    "Prefer retrieve() before making assumptions. Use calculator() for any arithmetic. "
    "STOP when the task is complete."
)

MAX_STEPS = 6


def run_agent(task: str):
    load_dotenv()
    model = os.getenv("MODEL", "gpt-4o-mini")
    base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("Set OPENAI_API_KEY in your environment")

    client = OpenAI(api_key=api_key, base_url=base_url)

    memory = Memory()
    memory.add("system", SYSTEM_PROMPT)
    memory.add("user", task)

    # Ensure tools are of type List[ChatCompletionToolUnionParam]
    from openai.types.chat import ChatCompletionToolParam
    tools = [ChatCompletionToolParam(**spec) for spec in all_openai_specs()]

    for step in range(1, MAX_STEPS + 1):
        resp = client.chat.completions.create(
            model=model,
            messages=[ChatCompletionMessageParam(**msg) for msg in memory.as_list()],
            tools=tools,
            tool_choice="auto",
            temperature=0.2,
        )
        msg = resp.choices[0].message

        # If the model wants to call tools
        if msg.tool_calls:
            memory.add("assistant", content=None)  # content omitted when using tool_calls
            for tool_call in msg.tool_calls:
                if tool_call.type == 'function':
                    name = tool_call.function.name
                    args = json.loads(tool_call.function.arguments)
                elif tool_call.type == 'custom' and hasattr(tool_call, 'custom'):
                    name = tool_call.type
                    # Access the input field for custom tools
                    args = json.loads(tool_call.custom.input)
                else:
                    # Handle unexpected tool call type
                    name = getattr(tool_call, 'type', 'unknown')
                    args = {}
                result = call_tool(name, json.dumps(args))
                memory.add(
                    "tool",
                    content=result,
                    tool_call_id=tool_call.id,
                )
            continue  # loop again with tool results in memory

        # Otherwise, we got a final answer
        if msg.content:
            memory.add("assistant", msg.content)
            print("\n=== FINAL ANSWER ===\n")
            print(msg.content)
            return

    # Step cap reached
    print("\n[!] Reached step limit without a final answer. Here's the latest context:\n")
    print(json.dumps(memory.as_list()[-6:], indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--task", required=True, help="User task for the agent")
    args = parser.parse_args()
    run_agent(args.task)

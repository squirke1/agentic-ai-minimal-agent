from __future__ import annotations
import argparse, json, os
import openai
from dotenv import load_dotenv
from memory import Memory
from tools import all_openai_specs, call_tool

SYSTEM_PROMPT = (
    "You are an autonomous but careful AI agent. "
    "Plan tasks, call tools when helpful, and finish with a concise, well-structured answer. "
    "Prefer retrieve() before making assumptions. Use calculator() for any arithmetic. "
    "STOP when the task is complete."
)

MAX_STEPS = 6


def run_agent(task: str):
    load_dotenv()
    model = os.getenv("MODEL", "gpt-4")  # Default to gpt-4 if not specified
    openai.api_key = os.getenv("OPENAI_API_KEY")
    openai.api_base = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    
    if not openai.api_key:
        raise RuntimeError("Set OPENAI_API_KEY in your environment")

    memory = Memory()
    memory.add("system", SYSTEM_PROMPT)
    memory.add("user", task)

    # Get the tools specification
    tools = all_openai_specs()

    for step in range(1, MAX_STEPS + 1):
        # Create the completion
        resp = openai.ChatCompletion.create(
            model=model,
            messages=memory.as_list(),
            functions=tools,
            function_call="auto",
            temperature=0.2,
        )
        # If resp is a generator, convert to list and get the first item
        if not isinstance(resp, dict):
            resp = dict(list(resp)[0])
        msg = resp['choices'][0]['message']

        # If the model wants to call a function
        if hasattr(msg, 'function_call') and msg.function_call:
            memory.add("assistant", content=None)  # content omitted when using function_call
            name = msg.function_call.name
            args = msg.function_call.arguments
            result = call_tool(name, args)
            memory.add(
                "tool",
                content=result,
                name=name,
            )
            continue  # loop again with tool results in memory

        # Otherwise, we got a final answer
        if hasattr(msg, 'content') and msg.content:
            memory.add("assistant", msg.content)
            print("\n=== FINAL ANSWER ===\n")
            print(msg['content'])
            return

    # Step cap reached
    print("\n[!] Reached step limit without a final answer. Here's the latest context:\n")
    print(json.dumps(memory.as_list()[-6:], indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--task", required=True, help="User task for the agent")
    args = parser.parse_args()
    run_agent(args.task)

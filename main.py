from __future__ import annotations
import argparse, json, os
import openai
from dotenv import load_dotenv
from memory import Memory
from tools import all_openai_specs, call_tool, get_vector_memory
from typing import Any, Dict

SYSTEM_PROMPT = (
    "You are an autonomous but careful AI agent with access to long-term memory. "
    "Plan tasks, call tools when helpful, and finish with a concise, well-structured answer. "
    "You can use search_memory() to find relevant past experiences and store_memory() to save important information. "
    "Prefer retrieve() for local docs and search_memory() for past experiences before making assumptions. "
    "Use calculator() for any arithmetic. "
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

    # Initialize long-term memory
    vector_memory = get_vector_memory()
    relevant_memories = []
    if vector_memory:
        print(f"Long-term memory initialized with {vector_memory.collection.count()} existing memories")
        
        # Search for relevant past experiences
        relevant_memories = vector_memory.search_memories(task, n_results=3, min_importance=0.6)
        if relevant_memories:
            print(f"Found {len(relevant_memories)} relevant memories from past experiences")
    else:
        print("Long-term memory not available. Install: pip install chromadb sentence-transformers")

    memory = Memory()
    memory.add("system", SYSTEM_PROMPT)
    
    # Add relevant past experiences to context if available
    if vector_memory and relevant_memories:
        context_str = "Relevant past experiences:\n"
        for mem in relevant_memories[:2]:  # Limit to top 2 to avoid token overflow
            context_str += f"- {mem['content'][:200]}...\n"
        memory.add("system", context_str)
    
    memory.add("user", task)

    # Get the tools specification
    tools = all_openai_specs()

    final_answer = None
    for step in range(1, MAX_STEPS + 1):
        print(f"\n--- Step {step} ---")
        
        try:
            # Create the completion
            resp = openai.ChatCompletion.create(
                model=model,
                messages=memory.as_list(),
                functions=tools,
                function_call="auto",
                temperature=0.2,
            )
            
            # For openai v0.28.x, response should be a dict-like object
            # Access the message directly
            msg = resp['choices'][0]['message']  # type: ignore
            
            # Check for function call
            if 'function_call' in msg and msg['function_call']:
                # Add assistant message with function call
                assistant_msg = {"role": "assistant", "function_call": msg['function_call']}
                memory.messages.append(assistant_msg)
                name = msg['function_call']['name']
                args = msg['function_call']['arguments']
                print(f"Calling tool: {name}")
                result = call_tool(name, args)
                # For OpenAI v0.28.x, use "function" role instead of "tool" 
                function_response = {
                    "role": "function",
                    "name": name,
                    "content": result
                }
                memory.messages.append(function_response)
                continue  # loop again with tool results in memory

            # Otherwise, we got a final answer
            if 'content' in msg and msg['content']:
                final_answer = msg['content']
                memory.add("assistant", msg['content'])
                print("\n=== FINAL ANSWER ===\n")
                print(msg['content'])
                break
            else:
                print("No content in message, continuing...")
                
        except KeyError as e:
            print(f"Response format error in step {step}: {e}")
            print(f"Response: {resp}")
            break
        except Exception as e:
            print(f"Error in step {step}: {e}")
            # For API errors (like quota), break the loop
            if "quota" in str(e).lower() or "rate limit" in str(e).lower():
                print("API quota/rate limit reached. Please check your OpenAI billing.")
                break
            continue

    # Store the task and result in long-term memory for future reference
    if vector_memory and final_answer:
        try:
            # Store the experience
            experience = f"Task: {task}\nResult: {final_answer[:500]}..."
            vector_memory.store_memory(
                content=experience,
                memory_type="experience",
                importance=0.7,
                metadata={"task_type": "user_request", "success": True}
            )
            print("\n[Memory] Stored experience in long-term memory")
        except Exception as e:
            print(f"\n[Memory] Failed to store experience: {e}")
    
    if final_answer is None:
        # Step cap reached
        print("\n[!] Reached step limit without a final answer. Here's the latest context:\n")
        print(json.dumps(memory.as_list()[-6:], indent=2))
        
        # Store incomplete attempt in memory with lower importance
        if vector_memory:
            try:
                incomplete_experience = f"Incomplete task: {task}\nReached step limit after {MAX_STEPS} steps"
                vector_memory.store_memory(
                    content=incomplete_experience,
                    memory_type="experience",
                    importance=0.3,
                    metadata={"task_type": "user_request", "success": False, "reason": "step_limit"}
                )
                print("\n[Memory] Stored incomplete attempt in long-term memory")
            except Exception as e:
                print(f"\n[Memory] Failed to store incomplete attempt: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--task", required=True, help="User task for the agent")
    args = parser.parse_args()
    run_agent(args.task)

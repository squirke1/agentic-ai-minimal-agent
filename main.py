"""Main agent execution module.

This module provides the core agent functionality that orchestrates
LLM-based planning and tool execution with persistent memory capabilities.
"""

from __future__ import annotations
import argparse, json, os
import openai
from dotenv import load_dotenv
from memory import Memory
from tools import all_openai_specs, call_tool, get_vector_memory
from typing import Any, Dict

# System prompt that defines the agent's behavior and capabilities
SYSTEM_PROMPT = (
    "You are an autonomous but careful AI agent with access to long-term memory. "
    "Plan tasks, call tools when helpful, and finish with a concise, well-structured answer. "
    "You can use search_memory() to find relevant past experiences and store_memory() to save important information. "
    "Prefer retrieve() for local docs and search_memory() for past experiences before making assumptions. "
    "Use calculator() for any arithmetic. "
    "STOP when the task is complete."
)

# Maximum number of reasoning steps to prevent infinite loops
MAX_STEPS = 6


def run_agent(task: str):
    """Execute an agent task using LLM planning and tool execution.
    
    This function implements a planner-executor loop where the LLM decides
    which tools to call and the runtime executes them. The agent maintains
    both short-term conversation memory and persistent long-term memory.
    
    Args:
        task: The user task to be completed by the agent
        
    Raises:
        RuntimeError: If OpenAI API key is not configured
        
    The agent will:
    1. Initialize memory systems (short-term and long-term)
    2. Search for relevant past experiences
    3. Execute up to MAX_STEPS reasoning cycles
    4. Store the experience for future reference
    """
    # Load environment configuration
    load_dotenv()
    model = os.getenv("MODEL", "gpt-4")  # Default to gpt-4 if not specified
    openai.api_key = os.getenv("OPENAI_API_KEY")
    openai.api_base = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    
    if not openai.api_key:
        raise RuntimeError("Set OPENAI_API_KEY in your environment")

    # Initialize long-term memory system for persistent learning
    vector_memory = get_vector_memory()
    relevant_memories = []
    if vector_memory:
        print(f"Long-term memory initialized with {vector_memory.collection.count()} existing memories")
        
        # Search for contextually relevant past experiences
        # This helps the agent learn from similar previous tasks
        relevant_memories = vector_memory.search_memories(task, n_results=3, min_importance=0.6)
        if relevant_memories:
            print(f"Found {len(relevant_memories)} relevant memories from past experiences")
    else:
        print("Long-term memory not available. Install: pip install chromadb sentence-transformers")

    # Initialize short-term conversation memory
    memory = Memory()
    memory.add("system", SYSTEM_PROMPT)
    
    # Inject relevant past experiences into the conversation context
    # This allows the agent to build on previous knowledge
    if vector_memory and relevant_memories:
        context_str = "Relevant past experiences:\n"
        for mem in relevant_memories[:2]:  # Limit to top 2 to avoid token overflow
            context_str += f"- {mem['content'][:200]}...\n"
        memory.add("system", context_str)
    
    # Add the user's task to conversation memory
    memory.add("user", task)

    # Get available tools for the agent to use
    tools = all_openai_specs()

    final_answer = None
    
    # Main reasoning loop: agent plans and executes until task completion
    for step in range(1, MAX_STEPS + 1):
        print(f"\n--- Step {step} ---")
        
        try:
            # Request LLM to analyze current state and decide next action
            resp = openai.ChatCompletion.create(
                model=model,
                messages=memory.as_list(),
                functions=tools,
                function_call="auto",
                temperature=0.2,
            )
            
            # Parse response from OpenAI v0.28.x format
            msg = resp['choices'][0]['message']  # type: ignore
            
            # Handle tool/function calling
            if 'function_call' in msg and msg['function_call']:
                # Add assistant's function call to conversation history
                assistant_msg = {"role": "assistant", "function_call": msg['function_call']}
                memory.messages.append(assistant_msg)
                
                # Extract tool name and arguments
                name = msg['function_call']['name']
                args = msg['function_call']['arguments']
                print(f"Calling tool: {name}")
                
                # Execute the requested tool
                result = call_tool(name, args)
                
                # Add tool result to conversation memory (v0.28.x format)
                function_response = {
                    "role": "function",
                    "name": name,
                    "content": result
                }
                memory.messages.append(function_response)
                continue  # Continue reasoning loop with tool results

            # Handle final answer from the agent
            if 'content' in msg and msg['content']:
                final_answer = msg['content']
                memory.add("assistant", msg['content'])
                print("\n=== FINAL ANSWER ===\n")
                print(msg['content'])
                break
            else:
                print("No content in message, continuing...")
                
        except KeyError as e:
            # Handle malformed API responses
            print(f"Response format error in step {step}: {e}")
            print(f"Response: {resp}")
            break
        except Exception as e:
            # Handle API errors and other exceptions
            print(f"Error in step {step}: {e}")
            # Break on quota/rate limit errors as they won't resolve by retrying
            if "quota" in str(e).lower() or "rate limit" in str(e).lower():
                print("API quota/rate limit reached. Please check your OpenAI billing.")
                break
            continue

    # Store completed task in long-term memory for future learning
    if vector_memory and final_answer:
        try:
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
    
    # Handle case where agent reaches step limit without completing task
    if final_answer is None:
        print("\n[!] Reached step limit without a final answer. Here's the latest context:\n")
        print(json.dumps(memory.as_list()[-6:], indent=2))
        
        # Store incomplete attempt for analysis and future improvement
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
    
    # Return the final answer or a default message if none was generated
    return final_answer or "I wasn't able to complete that request. Please try rephrasing or check the system status."


if __name__ == "__main__":
    """Command-line interface for the agent."""
    parser = argparse.ArgumentParser(
        description="Run an autonomous AI agent with memory capabilities"
    )
    parser.add_argument("--task", required=True, help="User task for the agent")
    args = parser.parse_args()
    run_agent(args.task)

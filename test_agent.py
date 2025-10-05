#!/usr/bin/env python3

"""
Test script for the agent without needing a real OpenAI API key
"""

from __future__ import annotations
import argparse, json, os
from dotenv import load_dotenv
from memory import Memory
from tools import all_openai_specs, call_tool, get_vector_memory

def mock_run_agent(task: str):
    """Test the agent without making API calls"""
    load_dotenv()
    
    print(f"Testing agent with task: {task}")
    
    # Initialize long-term memory
    vector_memory = get_vector_memory()
    if vector_memory:
        print(f"Long-term memory initialized with {vector_memory.collection.count()} existing memories")
        
        # Test memory operations
        print("\n--- Testing Memory Operations ---")
        
        # Store a test memory
        memory_id = vector_memory.store_memory(
            content="This is a test memory about AI agents",
            memory_type="fact",
            importance=0.8
        )
        print(f"Stored test memory: {memory_id}")
        
        # Search for memories
        results = vector_memory.search_memories("AI agents", n_results=2)
        print(f"Found {len(results)} memories about AI agents")
        
        # Get stats
        stats = vector_memory.get_memory_stats()
        print(f"Memory stats: {stats}")
        
    else:
        print("❌ Long-term memory not available")

    # Test tools
    print("\n--- Testing Tools ---")
    tools = all_openai_specs()
    print(f"Loaded {len(tools)} tools:")
    for tool in tools:
        print(f"   - {tool['name']}: {tool['description']}")
    
    # Test calculator
    calc_result = call_tool("calculator", '{"expression": "2 + 2 * 3"}')
    print(f"Calculator test: {calc_result}")
    
    # Test memory tools if available
    if vector_memory:
        memory_result = call_tool("memory_stats", '{}')
        print(f"Memory stats tool: {memory_result}")
    
    print("\nAll tests completed successfully.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--task", default="Test all systems", help="Task to test")
    args = parser.parse_args()
    mock_run_agent(args.task)
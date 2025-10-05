#!/usr/bin/env python3

"""
Demo script showing how the agent works with all systems
This simulates the agent flow without needing OpenAI API
"""

from __future__ import annotations
import json
from memory import Memory
from tools import all_openai_specs, call_tool, get_vector_memory

def demo_agent_workflow():
    """Demonstrate the complete agent workflow"""
    
    print("Agentic AI Agent Demo")
    print("=" * 40)
    
    # Task
    task = "Help me understand how long-term memory works in AI agents"
    print(f"Task: {task}\n")
    
    # Initialize systems
    print("1. Initializing Systems...")
    vector_memory = get_vector_memory()
    memory = Memory()
    tools = all_openai_specs()
    
    print(f"Long-term memory: {vector_memory.collection.count() if vector_memory else 0} existing memories")
    print(f"Available tools: {len(tools)}")
    print(f"Short-term memory initialized\n")
    
    # Simulate agent steps
    print("2. Agent Planning & Execution...")
    
    # Step 1: Search for relevant memories
    print("Step 1: Searching long-term memory...")
    if vector_memory:
        relevant_memories = vector_memory.search_memories("long-term memory AI", n_results=3)
        print(f"   Found {len(relevant_memories)} relevant memories")
        
        if not relevant_memories:
            print("   No relevant memories found, agent will learn from scratch")
    
    # Step 2: Use retrieve tool to get local docs
    print("\nStep 2: Searching local documentation...")
    retrieve_result = call_tool("retrieve", '{"query": "long-term memory AI agent", "k": 2}')
    retrieve_data = json.loads(retrieve_result)
    print(f"   Found {len(retrieve_data.get('hits', []))} relevant documents")
    
    # Step 3: Use calculator for any computations
    print("\nStep 3: Calculating memory efficiency...")
    calc_result = call_tool("calculator", '{"expression": "1000 * 0.85"}')
    calc_data = json.loads(calc_result)
    print(f"   Calculation result: {calc_data.get('result', 0)} effective memories")
    
    # Step 4: Generate response (simulated)
    print("\nStep 4: Generating response...")
    response = """
Long-term memory in AI agents works through several key mechanisms:

1. **Vector Storage**: Memories are converted to embeddings and stored in a vector database
2. **Semantic Search**: Related memories are found using similarity matching
3. **Importance Scoring**: Memories have importance weights (0.0-1.0) for prioritization
4. **Memory Types**: Different categories like experiences, facts, skills, and conversations
5. **Persistent Storage**: Memories survive across agent sessions

Benefits:
- Agents can learn from past experiences
- Improved performance on similar tasks
- Better context awareness and continuity
- Reduced repetition of solved problems

The system automatically stores successful task completions and can retrieve
relevant past experiences when facing new challenges.
    """
    
    print("Response generated!")
    
    # Step 5: Store the experience
    print("\nStep 5: Storing experience in long-term memory...")
    if vector_memory:
        experience = f"Task: {task}\nResponse: {response[:200]}..."
        memory_id = vector_memory.store_memory(
            content=experience,
            memory_type="experience",
            importance=0.8,
            metadata={"task_type": "explanation", "topic": "long-term memory"}
        )
        print(f"Stored experience: {memory_id}")
    
    # Final stats
    print("\n3. Final Statistics...")
    if vector_memory:
        stats = vector_memory.get_memory_stats()
        print(f"Total memories: {stats['total_memories']}")
        print(f"Memory types: {stats['memory_types']}")
        print(f"Average importance: {stats['average_importance']}")
    
    print("\n" + "=" * 40)
    print("Demo completed. The agent:")
    print("   - Searched existing memories for context")
    print("   - Retrieved relevant documentation") 
    print("   - Performed calculations")
    print("   - Generated a detailed response")
    print("   - Stored the experience for future reference")
    
    print(f"\nFinal Response:\n{response}")

if __name__ == "__main__":
    demo_agent_workflow()
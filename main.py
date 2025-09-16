"""
Minimal Agentic AI Agent
A simple implementation of an agentic AI system with tools, memory, and conversation capabilities.
"""

import os
import json
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv
import openai

from memory import Memory
from tools import ToolRegistry


class MinimalAgent:
    """
    A minimal agentic AI agent with tool calling capabilities and memory.
    """
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-3.5-turbo"):
        """
        Initialize the agent.
        
        Args:
            api_key: OpenAI API key (if not provided, will try to load from environment)
            model: OpenAI model to use
        """
        # Load environment variables
        load_dotenv()
        
        # Set up OpenAI client
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable or pass api_key parameter.")
        
        self.client = openai.OpenAI(api_key=self.api_key)
        self.model = model
        
        # Initialize components
        self.memory = Memory(limit=int(os.getenv("MEMORY_LIMIT", 100)))
        self.tool_registry = ToolRegistry()
        
        # Agent configuration
        self.name = os.getenv("AGENT_NAME", "MinimalAgent")
        self.max_iterations = int(os.getenv("MAX_ITERATIONS", 10))
        self.temperature = float(os.getenv("TEMPERATURE", 0.7))
        
        # System prompt
        self.system_prompt = f"""You are {self.name}, a helpful AI assistant with access to various tools.
You can help users with calculations, file operations, web requests, and more.

Available tools:
{', '.join(self.tool_registry.list_tools())}

Always think step by step and use tools when appropriate to help the user.
Be precise and helpful in your responses."""
        
        # Add system prompt to memory
        self.memory.add_entry("system", self.system_prompt)
    
    def chat(self, user_input: str) -> str:
        """
        Process user input and return agent response.
        
        Args:
            user_input: User's message
            
        Returns:
            Agent's response
        """
        # Add user input to memory
        self.memory.add_entry("user", user_input)
        
        # Process the conversation with tool calling
        response = self._process_with_tools()
        
        # Add assistant response to memory
        self.memory.add_entry("assistant", response)
        
        return response
    
    def _process_with_tools(self) -> str:
        """
        Process the conversation with tool calling support.
        
        Returns:
            Final response from the agent
        """
        messages = self.memory.get_conversation_history()
        functions = self.tool_registry.get_openai_functions()
        
        iteration = 0
        while iteration < self.max_iterations:
            try:
                # Make API call with function calling
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    functions=functions,
                    function_call="auto",
                    temperature=self.temperature
                )
                
                message = response.choices[0].message
                
                # Check if the model wants to call a function
                if message.function_call:
                    function_name = message.function_call.name
                    function_args = json.loads(message.function_call.arguments)
                    
                    # Execute the tool
                    tool_result = self.tool_registry.execute_tool(function_name, **function_args)
                    
                    # Add function call and result to conversation
                    messages.append({
                        "role": "assistant",
                        "content": None,
                        "function_call": {
                            "name": function_name,
                            "arguments": message.function_call.arguments
                        }
                    })
                    
                    messages.append({
                        "role": "function",
                        "name": function_name,
                        "content": json.dumps(tool_result)
                    })
                    
                    iteration += 1
                    continue
                
                # No function call, return the response
                return message.content
                
            except Exception as e:
                return f"Error processing request: {str(e)}"
        
        return "Maximum iterations reached. Please try simplifying your request."
    
    def get_available_tools(self) -> List[str]:
        """Get list of available tools."""
        return self.tool_registry.list_tools()
    
    def clear_memory(self):
        """Clear the agent's memory."""
        self.memory.clear()
        self.memory.add_entry("system", self.system_prompt)
    
    def save_memory(self, filepath: str):
        """Save memory to file."""
        self.memory.save_to_file(filepath)
    
    def load_memory(self, filepath: str):
        """Load memory from file."""
        self.memory.load_from_file(filepath)
        # Ensure system prompt is present
        conversation = self.memory.get_conversation_history()
        if not conversation or conversation[0]["role"] != "system":
            self.memory.add_entry("system", self.system_prompt)


def main():
    """Main function for running the agent interactively."""
    print("=== Minimal Agentic AI Agent ===")
    print("Type 'quit' to exit, 'clear' to clear memory, 'tools' to list available tools")
    print()
    
    try:
        agent = MinimalAgent()
        print(f"Agent '{agent.name}' initialized successfully!")
        print(f"Available tools: {', '.join(agent.get_available_tools())}")
        print()
        
        while True:
            try:
                user_input = input("You: ").strip()
                
                if user_input.lower() == 'quit':
                    print("Goodbye!")
                    break
                elif user_input.lower() == 'clear':
                    agent.clear_memory()
                    print("Memory cleared!")
                    continue
                elif user_input.lower() == 'tools':
                    print(f"Available tools: {', '.join(agent.get_available_tools())}")
                    continue
                elif not user_input:
                    continue
                
                print(f"{agent.name}: ", end="", flush=True)
                response = agent.chat(user_input)
                print(response)
                print()
                
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except Exception as e:
                print(f"Error: {str(e)}")
                print()
    
    except Exception as e:
        print(f"Failed to initialize agent: {str(e)}")
        print("Make sure you have set your OPENAI_API_KEY in the .env file")


if __name__ == "__main__":
    main()
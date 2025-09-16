"""
Tool definitions and implementations for the minimal agentic AI agent.
Provides basic tools for file operations, web requests, and calculations.
"""

import json
import os
import requests
from typing import Dict, Any, List, Callable
from datetime import datetime
import math


class Tool:
    """Base class for agent tools."""
    
    def __init__(self, name: str, description: str, parameters: Dict[str, Any]):
        self.name = name
        self.description = description
        self.parameters = parameters
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute the tool with given parameters."""
        raise NotImplementedError("Tool must implement execute method")
    
    def to_openai_function(self) -> Dict[str, Any]:
        """Convert tool to OpenAI function format."""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters
        }


class CalculatorTool(Tool):
    """Tool for performing mathematical calculations."""
    
    def __init__(self):
        super().__init__(
            name="calculator",
            description="Perform mathematical calculations",
            parameters={
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "Mathematical expression to evaluate (e.g., '2 + 3 * 4')"
                    }
                },
                "required": ["expression"]
            }
        )
    
    def execute(self, expression: str) -> Dict[str, Any]:
        """Execute mathematical calculation."""
        try:
            # Safe evaluation of mathematical expressions
            # Only allow basic math operations and functions
            allowed_names = {
                k: v for k, v in math.__dict__.items() 
                if not k.startswith("__")
            }
            allowed_names.update({"abs": abs, "round": round})
            
            result = eval(expression, {"__builtins__": {}}, allowed_names)
            return {
                "success": True,
                "result": result,
                "expression": expression
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "expression": expression
            }


class FileReaderTool(Tool):
    """Tool for reading file contents."""
    
    def __init__(self):
        super().__init__(
            name="read_file",
            description="Read the contents of a text file",
            parameters={
                "type": "object",
                "properties": {
                    "filepath": {
                        "type": "string",
                        "description": "Path to the file to read"
                    }
                },
                "required": ["filepath"]
            }
        )
    
    def execute(self, filepath: str) -> Dict[str, Any]:
        """Read file contents."""
        try:
            if not os.path.exists(filepath):
                return {
                    "success": False,
                    "error": f"File not found: {filepath}"
                }
            
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return {
                "success": True,
                "content": content,
                "filepath": filepath,
                "size": len(content)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "filepath": filepath
            }


class FileWriterTool(Tool):
    """Tool for writing content to files."""
    
    def __init__(self):
        super().__init__(
            name="write_file",
            description="Write content to a text file",
            parameters={
                "type": "object",
                "properties": {
                    "filepath": {
                        "type": "string",
                        "description": "Path to the file to write"
                    },
                    "content": {
                        "type": "string",
                        "description": "Content to write to the file"
                    }
                },
                "required": ["filepath", "content"]
            }
        )
    
    def execute(self, filepath: str, content: str) -> Dict[str, Any]:
        """Write content to file."""
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return {
                "success": True,
                "filepath": filepath,
                "bytes_written": len(content.encode('utf-8'))
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "filepath": filepath
            }


class WebRequestTool(Tool):
    """Tool for making HTTP requests."""
    
    def __init__(self):
        super().__init__(
            name="web_request",
            description="Make HTTP requests to web URLs",
            parameters={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "URL to make request to"
                    },
                    "method": {
                        "type": "string",
                        "description": "HTTP method (GET, POST, etc.)",
                        "default": "GET"
                    }
                },
                "required": ["url"]
            }
        )
    
    def execute(self, url: str, method: str = "GET") -> Dict[str, Any]:
        """Make HTTP request."""
        try:
            response = requests.request(method, url, timeout=10)
            
            return {
                "success": True,
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "content": response.text[:1000],  # Limit content size
                "url": url,
                "method": method
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "url": url,
                "method": method
            }


class TimeTool(Tool):
    """Tool for getting current time and date information."""
    
    def __init__(self):
        super().__init__(
            name="get_time",
            description="Get current time and date information",
            parameters={
                "type": "object",
                "properties": {
                    "format": {
                        "type": "string",
                        "description": "Time format ('iso', 'human', 'timestamp')",
                        "default": "human"
                    }
                }
            }
        )
    
    def execute(self, format: str = "human") -> Dict[str, Any]:
        """Get current time."""
        try:
            now = datetime.now()
            
            if format == "iso":
                time_str = now.isoformat()
            elif format == "timestamp":
                time_str = str(now.timestamp())
            else:  # human format
                time_str = now.strftime("%Y-%m-%d %H:%M:%S")
            
            return {
                "success": True,
                "time": time_str,
                "format": format,
                "timestamp": now.timestamp()
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "format": format
            }


class ToolRegistry:
    """Registry for managing available tools."""
    
    def __init__(self):
        self.tools = {}
        self._register_default_tools()
    
    def _register_default_tools(self):
        """Register default tools."""
        default_tools = [
            CalculatorTool(),
            FileReaderTool(),
            FileWriterTool(),
            WebRequestTool(),
            TimeTool()
        ]
        
        for tool in default_tools:
            self.register_tool(tool)
    
    def register_tool(self, tool: Tool):
        """Register a tool in the registry."""
        self.tools[tool.name] = tool
    
    def get_tool(self, name: str) -> Tool:
        """Get a tool by name."""
        return self.tools.get(name)
    
    def list_tools(self) -> List[str]:
        """List all available tool names."""
        return list(self.tools.keys())
    
    def get_openai_functions(self) -> List[Dict[str, Any]]:
        """Get all tools formatted for OpenAI function calling."""
        return [tool.to_openai_function() for tool in self.tools.values()]
    
    def execute_tool(self, name: str, **kwargs) -> Dict[str, Any]:
        """Execute a tool by name with given parameters."""
        tool = self.get_tool(name)
        if not tool:
            return {
                "success": False,
                "error": f"Tool '{name}' not found"
            }
        
        try:
            return tool.execute(**kwargs)
        except Exception as e:
            return {
                "success": False,
                "error": f"Error executing tool '{name}': {str(e)}"
            }
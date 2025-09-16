# Minimal Agentic AI Agent

A minimal implementation of an agentic AI system with tool calling capabilities, memory management, and conversation handling. This project demonstrates the core concepts of building AI agents that can interact with tools and maintain conversational context.

## Features

- **Tool Integration**: Built-in tools for calculations, file operations, web requests, and time queries
- **Memory Management**: Maintains conversation history and context across interactions
- **Function Calling**: Uses OpenAI's function calling capabilities for structured tool interactions
- **Extensible Architecture**: Easy to add new tools and capabilities
- **Interactive CLI**: Command-line interface for direct interaction with the agent

## Quick Start

### Prerequisites

- Python 3.8+
- OpenAI API key

### Installation

1. Clone the repository:
```bash
git clone https://github.com/squirke1/agentic-ai-minimal-agent.git
cd agentic-ai-minimal-agent
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

4. Run the agent:
```bash
python main.py
```

## Project Structure

```
agentic-ai-minimal-agent/
├── README.md              # This file
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
├── main.py               # Main agent implementation and CLI
├── tools.py              # Tool definitions and registry
├── memory.py             # Memory management system
└── docs/
    └── sample_notes.md   # Usage examples and documentation
```

## Available Tools

- **Calculator**: Perform mathematical calculations
- **File Reader**: Read contents of text files
- **File Writer**: Write content to files
- **Web Request**: Make HTTP requests to URLs
- **Time**: Get current date and time information

## Usage Examples

### Basic Interaction
```
You: What is 15 * 7 + 32?
MinimalAgent: I'll calculate that for you.
The result of 15 * 7 + 32 is 137.
```

### File Operations
```
You: Create a file called notes.txt with "Hello World"
MinimalAgent: I'll create that file for you.
I've successfully created the file "notes.txt" with the content "Hello World".
```

### Web Requests
```
You: Check if example.com is accessible
MinimalAgent: I'll make a request to example.com to check accessibility.
Yes, example.com is accessible with status code 200.
```

## Configuration

Configure the agent through environment variables in your `.env` file:

- `OPENAI_API_KEY`: Your OpenAI API key (required)
- `AGENT_NAME`: Name of the agent (default: MinimalAgent)
- `MAX_ITERATIONS`: Maximum tool calling iterations (default: 10)
- `TEMPERATURE`: Response creativity (default: 0.7)
- `MEMORY_LIMIT`: Maximum memory entries (default: 100)

## Interactive Commands

When running the agent interactively:
- `quit`: Exit the program
- `clear`: Clear conversation memory
- `tools`: List available tools

## Architecture

### Core Components

1. **MinimalAgent**: Main agent class that orchestrates conversation and tool usage
2. **Memory**: Manages conversation history and context
3. **ToolRegistry**: Manages available tools and their execution
4. **Tool**: Base class for implementing new tools

### Adding New Tools

To add a new tool, create a class that inherits from `Tool`:

```python
class MyCustomTool(Tool):
    def __init__(self):
        super().__init__(
            name="my_tool",
            description="Description of what the tool does",
            parameters={
                "type": "object",
                "properties": {
                    "param": {
                        "type": "string",
                        "description": "Parameter description"
                    }
                },
                "required": ["param"]
            }
        )
    
    def execute(self, param: str) -> Dict[str, Any]:
        # Tool implementation
        return {"success": True, "result": "Tool output"}
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add your changes
4. Ensure all tests pass
5. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Documentation

For more detailed examples and usage patterns, see [docs/sample_notes.md](docs/sample_notes.md).
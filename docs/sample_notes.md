# Sample Notes for Minimal Agentic AI Agent

## Overview

This document provides sample usage patterns and examples for the Minimal Agentic AI Agent.

## Basic Usage Examples

### Starting a Conversation

```
You: Hello, can you help me with some calculations?
MinimalAgent: Hello! I'd be happy to help you with calculations. I have access to a calculator tool that can perform mathematical operations. What would you like me to calculate?
```

### Using the Calculator Tool

```
You: What is 15 * 7 + 32?
MinimalAgent: I'll calculate that for you.

The result of 15 * 7 + 32 is 137.
```

### File Operations

```
You: Can you create a file called "hello.txt" with the content "Hello, World!"?
MinimalAgent: I'll create that file for you.

I've successfully created the file "hello.txt" with the content "Hello, World!". The file is now saved and ready to use.
```

### Reading Files

```
You: Can you read the contents of hello.txt?
MinimalAgent: I'll read the file for you.

The contents of hello.txt are:
Hello, World!
```

### Getting Current Time

```
You: What time is it?
MinimalAgent: Let me get the current time for you.

The current time is 2024-01-15 14:30:45.
```

### Web Requests

```
You: Can you check if google.com is accessible?
MinimalAgent: I'll make a request to google.com to check if it's accessible.

Yes, google.com is accessible. The request returned a status code of 200, indicating the site is responding normally.
```

## Tool Capabilities

### Calculator Tool
- Supports basic arithmetic operations (+, -, *, /)
- Mathematical functions (sin, cos, sqrt, etc.)
- Constants (pi, e)
- Example: `2 + 3 * 4`, `sqrt(16)`, `sin(pi/2)`

### File Reader Tool
- Reads text files from the local filesystem
- Returns file content and metadata
- Handles encoding automatically

### File Writer Tool
- Writes content to text files
- Creates directories if they don't exist
- Returns success status and bytes written

### Web Request Tool
- Makes HTTP requests to URLs
- Supports different HTTP methods
- Returns response status, headers, and content preview

### Time Tool
- Gets current date and time
- Supports multiple formats (human-readable, ISO, timestamp)
- Useful for timestamping and scheduling

## Memory Management

The agent maintains conversation history and can:
- Remember previous interactions within the session
- Maintain context across multiple tool calls
- Store up to 100 conversation entries by default (configurable)

## Configuration Options

The agent can be configured through environment variables:

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

## Best Practices

1. **Be Specific**: Provide clear instructions for what you want the agent to do
2. **File Paths**: Use absolute paths or ensure files exist in the current directory
3. **Error Handling**: The agent will report errors and suggest alternatives
4. **Memory Management**: Clear memory periodically for long conversations
5. **API Limits**: Be mindful of OpenAI API usage and costs

## Troubleshooting

### Common Issues

1. **API Key Not Set**: Make sure OPENAI_API_KEY is configured in your .env file
2. **File Not Found**: Check file paths and permissions
3. **Network Errors**: Verify internet connection for web requests
4. **Tool Failures**: Check tool parameters and try again

### Error Messages

The agent provides descriptive error messages to help diagnose issues:
- Tool execution failures include specific error details
- API errors are caught and reported clearly
- File operation errors indicate the specific problem

## Example Session

```
=== Minimal Agentic AI Agent ===
Type 'quit' to exit, 'clear' to clear memory, 'tools' to list available tools

Agent 'MinimalAgent' initialized successfully!
Available tools: calculator, read_file, write_file, web_request, get_time

You: Can you calculate the area of a circle with radius 5?
MinimalAgent: I'll calculate the area of a circle with radius 5 for you.

The area of a circle with radius 5 is approximately 78.54 square units.
(Using the formula π × r², which gives us π × 5² = π × 25 ≈ 78.54)

You: Now save that result to a file called circle_area.txt
MinimalAgent: I'll save the circle area calculation result to a file for you.

I've successfully saved the circle area result to "circle_area.txt". The file contains the calculation details and result.

You: quit
Goodbye!
```

This example demonstrates the agent's ability to use multiple tools in sequence and maintain context throughout the conversation.
## Implementation Details: OpenAI Agents SDK, Model Context Protocol, and ChatKit UI

### **OpenAI Agents SDK**

The OpenAI Agents SDK is a production-ready framework for building agentic AI applications with minimal abstractions. It provides a lightweight, Python-first approach to creating intelligent systems that can understand instructions and take actions.[1]

#### Core Components

The SDK's fundamental primitives include:[1]

- **Agents**: LLMs equipped with instructions and tools that can execute tasks
- **Handoffs**: Allow agents to delegate to other agents for specific domain tasks
- **Guardrails**: Enable validation of agent inputs and outputs
- **Sessions**: Automatically maintain conversation history across agent runs
- **Tracing**: Built-in visualization and debugging for agentic flows

#### Installation

```bash
pip install openai-agents
```

#### Basic Agent Creation

The simplest way to create an agent requires just a few parameters:[1]

```python
from agents import Agent, Runner

agent = Agent(
    name="Assistant",
    instructions="You are a helpful assistant"
)

result = Runner.run_sync(agent, "Write a haiku about recursion in programming.")
print(result.final_output)
# Output: Code within the code, / Functions calling themselves, / Infinite loop's dance.
```

#### Advanced Agent Configuration

For more complex applications, you can configure model settings and tools:[1]

```python
from agents import Agent, ModelSettings

advanced_agent = Agent(
    name="Advanced Assistant",
    instructions="""You are a professional, concise assistant who always provides
    accurate information. When you don't know something, clearly state that.
    Focus on giving actionable insights when answering questions.""",
    model="gpt-4o",
    model_settings=ModelSettings(
        temperature=0.3,  # Lower for more deterministic outputs (0.0-2.0)
        max_tokens=1024,  # Maximum length of response
    ),
    tools=[]
)
```

#### Function Tools with @function_tool Decorator

The most powerful feature is turning Python functions into tools automatically using the `@function_tool` decorator. This decorator automatically generates JSON schemas from function signatures and docstrings:[2][3]

```python
from agents import Agent, Runner
from agents import function_tool

@function_tool
def get_weather(location: str, units: str = "celsius") -> str:
    """Get the current weather for a location.
    
    Args:
        location: The city or location name
        units: Temperature units - celsius or fahrenheit
    
    Returns:
        A string describing the current weather
    """
    # Implementation would call a weather API
    return f"Weather in {location}: 20°{units[0].upper()}"

@function_tool
def calculate_sum(a: int, b: int) -> int:
    """Add two numbers together."""
    return a + b

# Create an agent with these tools
agent = Agent(
    name="Weather Assistant",
    instructions="You are a helpful weather assistant. Use tools to get weather information.",
    tools=[get_weather, calculate_sum]
)

# Run the agent
result = Runner.run_sync(agent, "What's the weather like in London?")
print(result.final_output)
```

#### Structured Output with Pydantic Models

For complex data extraction, use Pydantic models:[1]

```python
from pydantic import BaseModel
from typing import List, Optional
from agents import Agent, Runner

class Person(BaseModel):
    name: str
    role: Optional[str]

class Meeting(BaseModel):
    date: str
    time: str
    location: Optional[str]
    duration: Optional[str]

class EmailData(BaseModel):
    subject: str
    sender: Person
    recipients: List[Person]
    main_points: List[str]
    meetings: List[Meeting]

# Agent configured for structured output
email_agent = Agent(
    name="Email Parser",
    instructions="Extract structured information from emails",
    output_type=EmailData
)

result = Runner.run_sync(email_agent, "Parse this email...")
print(f"Subject: {result.final_output.subject}")
```

#### Agent Handoffs and Specialization

Create specialized agents and have a coordinator delegate to them:[1]

```python
from agents import Agent, Runner

weather_agent = Agent(
    name="Weather Specialist",
    instructions="You are an expert in weather information"
)

finance_agent = Agent(
    name="Finance Specialist",
    instructions="You are an expert in financial analysis"
)

coordinator_agent = Agent(
    name="Coordinator",
    instructions="You coordinate between specialists",
    handoffs=[weather_agent, finance_agent]
)

# Agents as tools
weather_tool = weather_agent.as_tool(
    tool_name="ask_weather_specialist",
    description="Ask the weather specialist for weather information"
)

# The coordinator can now delegate tasks
```

***

### **Model Context Protocol (MCP)**

MCP is an open-source protocol developed by Anthropic that standardizes how LLMs connect to external data sources and tools, eliminating the need for custom integrations.[4][5]

#### Architecture Overview

MCP follows a client-server architecture with four primary components:[5]

1. **MCP Host**: The AI application (e.g., Claude Desktop, web-based chat)
2. **MCP Client**: Maintains connection to MCP servers, translates requirements
3. **MCP Server**: Exposes tools, resources, and prompts
4. **Transport Layer**: Handles communication between clients and servers

#### Transport Mechanisms

MCP supports two transport methods:[5]

- **STDIO**: Local process communication with optimal performance and no network overhead
- **HTTP+SSE**: Remote connections using HTTP POST requests and Server-Sent Events for streaming

#### Core Primitives

MCP defines three types of primitives that servers can expose:[5]

- **Tools**: Executable functions that AI applications can invoke (file operations, API calls, database queries)
- **Resources**: Data sources providing contextual information (file contents, database records)
- **Prompts**: Reusable templates for structuring LLM interactions

#### Basic MCP Server Implementation (Python)

Using FastMCP (simplified approach):[6]

```python
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
import os
import mysql.connector

load_dotenv('.env')

# Connect to MySQL database
mysql = mysql.connector.connect(
    host=os.getenv("DB_HOST"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_DATABASE")
)

# Create FastMCP server
mcp = FastMCP(name="Demo MySQL Server", host="0.0.0.0", port=8050)

# Define tools using @mcp.tool() decorator
@mcp.tool()
def show_tables() -> list:
    """List all tables in the database."""
    cursor = mysql.cursor()
    cursor.execute("SHOW TABLES")
    return cursor.fetchall()

@mcp.tool()
def query_database(sql: str) -> list:
    """Execute a custom SQL query."""
    cursor = mysql.cursor()
    cursor.execute(sql)
    return cursor.fetchall()

# Run server in stdio mode
if __name__ == "__main__":
    mcp.run(transport="stdio")
```

#### Advanced MCP Server Implementation (Node.js)

```javascript
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";

// Initialize server
const server = new McpServer({
    name: "mcp-weather-server",
    version: "1.0.0",
});

// Define tool with schema
server.setRequestHandler(ListToolsRequestSchema, async () => {
    return {
        tools: [
            {
                name: "get_weather",
                description: "Get current weather for a location",
                inputSchema: {
                    type: "object",
                    properties: {
                        location: {
                            type: "string",
                            description: "City name"
                        },
                        units: {
                            type: "string",
                            enum: ["celsius", "fahrenheit"]
                        }
                    },
                    required: ["location"]
                }
            }
        ]
    };
});

// Handle tool calls
server.setRequestHandler(CallToolRequestSchema, async (request) => {
    if (request.params.name === "get_weather") {
        const { location, units = "celsius" } = request.params.arguments;
        // Fetch weather data
        return {
            content: [{
                type: "text",
                text: `Weather in ${location}: 20°${units[0].toUpperCase()}`
            }]
        };
    }
});

// Run server
const transport = new StdioServerTransport();
await server.connect(transport);
```

#### MCP Protocol Handshake (JSON-RPC 2.0)

The initialization sequence between client and server:[5]

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "initialize",
  "params": {
    "protocolVersion": "2025-06-18",
    "capabilities": {
      "elicitation": {}
    },
    "clientInfo": {
      "name": "example-client",
      "version": "1.0.0"
    }
  }
}
```

Server response with capability negotiation:

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "protocolVersion": "2025-06-18",
    "capabilities": {
      "tools": { "listChanged": true },
      "resources": {}
    },
    "serverInfo": {
      "name": "mcp-server",
      "version": "1.0.0"
    }
  }
}
```

#### Tool Discovery and Execution

Clients discover available tools:[5]

```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "tools/list"
}
```

Server returns tool definitions:

```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "result": {
    "tools": [
      {
        "name": "weather_current",
        "title": "Get Current Weather",
        "description": "Retrieve current weather conditions",
        "inputSchema": {
          "type": "object",
          "properties": {
            "location": { "type": "string" },
            "units": { "type": "string", "enum": ["imperial", "metric"] }
          },
          "required": ["location"]
        }
      }
    ]
  }
}
```

Tool execution request:

```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "method": "tools/call",
  "params": {
    "name": "weather_current",
    "arguments": {
      "location": "San Francisco",
      "units": "imperial"
    }
  }
}
```

Tool execution response:

```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "San Francisco: 72°F, Partly cloudy"
      }
    ]
  }
}
```

***

### **ChatKit UI**

ChatKit is OpenAI's embeddable chat UI component that integrates with Agent Builder workflows to provide customizable chat experiences without requiring custom UI development.[7][8]

#### High-Level Architecture

ChatKit follows a three-step setup process:[7]

1. Create an agent workflow using OpenAI's Agent Builder
2. Set up ChatKit with session management
3. Embed ChatKit in your frontend with custom styling

#### Backend Session Management (FastAPI)

Create a session endpoint that generates client secrets:[7]

```python
from fastapi import FastAPI
from pydantic import BaseModel
from openai import OpenAI
import os

app = FastAPI()
openai = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

@app.post("/api/chatkit/session")
def create_chatkit_session():
    """Create a new ChatKit session."""
    session = openai.chatkit.sessions.create({
        "workflow": {
            "id": "wf_68df4b13b3588190a09d19288d4610ec0df388c3983f58d1"
        },
        "user": "user_identifier"
    })
    return {"client_secret": session.client_secret}

@app.post("/api/chatkit/refresh")
def refresh_chatkit_session(current_client_secret: str):
    """Refresh an existing ChatKit session."""
    session = openai.chatkit.sessions.refresh(current_client_secret)
    return {"client_secret": session.client_secret}
```

#### Frontend Implementation (React)

```typescript
import { ChatKit, useChatKit } from '@openai/chatkit-react';

export function MyChat() {
    const { control } = useChatKit({
        api: {
            async getClientSecret(existing) {
                if (existing) {
                    // Implement session refresh logic
                    const res = await fetch('/api/chatkit/refresh', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ currentClientSecret: existing })
                    });
                    const { client_secret } = await res.json();
                    return client_secret;
                }
                
                // Get new session
                const res = await fetch('/api/chatkit/session', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                });
                const { client_secret } = await res.json();
                return client_secret;
            },
        },
    });

    return (
        <ChatKit 
            control={control} 
            className="h-[600px] w-[320px]"
        />
    );
}
```

#### HTML/Vanilla JavaScript Integration

```html
<!DOCTYPE html>
<html>
<head>
    <script 
        src="https://cdn.platform.openai.com/deployments/chatkit/chatkit.js" 
        async>
    </script>
</head>
<body>
    <h1>Chat</h1>
    <openai-chatkit 
        id="chat" 
        style="height:560px;width:100%">
    </openai-chatkit>

    <script type="module">
        const chatEl = document.getElementById('chat');

        // Fetch client secret from backend
        async function getClientSecret() {
            const res = await fetch('/api/chatkit/session', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });
            const { client_secret } = await res.json();
            return client_secret;
        }

        // Configure ChatKit
        async function setupChat() {
            const token = await getClientSecret();
            
            chatEl.setOptions({
                auth: { token },
                theme: 'light',
                accentColor: '#2563EB',
                composerPlaceholder: 'Ask me anything…',
                startScreenPrompts: [
                    'Summarize this page',
                    'Draft an email',
                    'Explain a concept'
                ]
            });
        }

        // Event listeners
        chatEl.addEventListener('chatkit.response.start', () => {
            console.log('Response streaming started...');
        });

        chatEl.addEventListener('chatkit.error', (e) => {
            console.error('ChatKit error:', e.detail);
        });

        setupChat().catch(console.error);
    </script>
</body>
</html>
```

#### Next.js Integration with App Router

```typescript
// app/api/chatkit/token/route.ts
import { NextResponse } from 'next/server';

export async function GET() {
    // Authenticate user (implementation depends on your auth system)
    const userId = 'authenticated-user-id';
    
    // Issue a short-lived client token from your backend
    const token = await issueChatKitClientToken({ userId });
    
    return NextResponse.json({ token });
}

// app/components/ChatPage.tsx
'use client';

import { useEffect, useRef } from 'react';

export default function ChatPage() {
    const chatRef = useRef<any>(null);

    useEffect(() => {
        async function setupChat() {
            if (!chatRef.current) return;

            const tokenRes = await fetch('/api/chatkit/token');
            const { token } = await tokenRes.json();

            chatRef.current.setOptions({
                auth: { token },
                theme: 'light',
                accentColor: '#2563EB',
                composerPlaceholder: 'Ask me anything…',
            });
        }

        setupChat().catch(console.error);
    }, []);

    return (
        <section className="max-w-3xl mx-auto p-4">
            <h1 className="text-2xl font-semibold mb-4">Chat Assistant</h1>
            <openai-chatkit
                ref={chatRef}
                style={{ height: '560px', width: '100%' }}
            />
        </section>
    );
}
```

#### Customization and Theming

ChatKit supports extensive customization:[8]

```typescript
const { control } = useChatKit({
    api: { async getClientSecret() { /* ... */ } },
    theme: 'dark',  // 'light' | 'dark' | 'auto'
    accentColor: '#FF5733',
    composerPlaceholder: 'Type your message...',
    startScreenPrompts: [
        'What can you help with?',
        'Show me examples'
    ],
    // Enable response cancellation
    allowResponseCancellation: true,
    // Custom CSS classes
    className: 'custom-chatkit-container'
});
```

#### Key Features of ChatKit[8]

- **Deep UI Customization**: Match your app's look and feel
- **Built-in Response Streaming**: Interactive, natural conversations
- **Tool and Workflow Integration**: Visualize agentic actions and chain-of-thought reasoning
- **Rich Interactive Widgets**: Rendered directly in the chat
- **Attachment Handling**: File and image uploads
- **Thread and Message Management**: Organize complex conversations
- **Source Annotations**: Transparency and references for generated content

***

### **Integration Example: All Three Technologies Together**

Here's how you might integrate all three components in a real application:

```python
# 1. Create an OpenAI Agent with tools
from agents import Agent, function_tool, Runner
from openai import OpenAI

@function_tool
def search_database(query: str) -> str:
    """Search the database for information."""
    # Implementation
    return f"Results for '{query}'"

agent = Agent(
    name="Assistant",
    instructions="Help users by searching the database",
    tools=[search_database]
)

# 2. Set up ChatKit session endpoint
from fastapi import FastAPI
import os

app = FastAPI()
openai = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

@app.post("/api/chatkit/session")
def create_session():
    session = openai.chatkit.sessions.create({
        "workflow": {
            "id": "your_workflow_id"
        }
    })
    return {"client_secret": session.client_secret}

# 3. Optional: Connect MCP server for extended capabilities
# The MCP server exposes additional tools that the agent can use
```

***

### **Summary**

These three technologies work together to create powerful AI applications:

- **OpenAI Agents SDK**: Builds intelligent agents with tools and multi-agent coordination[9][1]
- **Model Context Protocol**: Standardizes how LLMs connect to external systems using JSON-RPC 2.0[10][4][5]
- **ChatKit UI**: Provides a production-ready chat interface with streaming, widgets, and customization[11][8][7]

Each technology can be used independently or combined for comprehensive agentic AI solutions.

[1](https://www.datacamp.com/tutorial/openai-agents-sdk-tutorial)
[2](https://codesignal.com/learn/courses/integrating-tools-into-openai-agents-in-python/lessons/creating-and-registering-custom-function-tools-for-openai-agents)
[3](https://openai.github.io/openai-agents-python/ref/tool/)
[4](https://www.descope.com/learn/post/mcp)
[5](https://modelcontextprotocol.io/docs/learn/architecture)
[6](https://www.coderslexicon.com/building-your-own-model-context-protocol-mcp-server-with-node-and-python/)
[7](https://platform.openai.com/docs/guides/chatkit)
[8](https://openai.github.io/chatkit-js/)
[9](https://platform.openai.com/docs/guides/agents-sdk)
[10](https://treblle.com/blog/model-context-protocol-guide)
[11](https://skywork.ai/blog/how-to-embed-custom-chatkit-chat-ui/)
[12](https://www.youtube.com/watch?v=mQHD3-mllro)
[13](https://openai.github.io/openai-agents-python/examples/)
[14](https://towardsdatascience.com/create-an-agent-with-openai-function-calling-capabilities-ad52122c3d12/)
[15](https://platform.openai.com/docs/guides/function-calling)
[16](https://www.youtube.com/watch?v=j5f2EQf5hkw)
[17](https://www.youtube.com/watch?v=47G1aEaNOKU)
[18](https://www.youtube.com/watch?v=euvQaIVpjq8)
[19](https://www.youtube.com/watch?v=8g0z3DNi_fU)
[20](https://www.buildwithmatija.com/blog/chatkit-nextjs-integration)
[21](https://www.youtube.com/watch?v=NT_ApmD_JPo)
[22](https://google.github.io/adk-docs/tools/mcp-tools/)
[23](https://www.reddit.com/r/mcp/comments/1ohskcw/list_of_tools_on_mcp_server/)
[24](https://www.youtube.com/watch?v=95OhwStbQUQ)
[25](https://modelcontextprotocol.info/docs/concepts/tools/)
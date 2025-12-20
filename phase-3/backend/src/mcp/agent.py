"""
AI Agent configuration.
Configures the agent with MCP tools and system instructions.
"""
import json
from typing import List, Dict, Any, Optional
from uuid import UUID
from sqlmodel import Session
from openai import OpenAI
from core.config import settings
from mcp.tools import add_task, list_tasks, complete_task, update_task, delete_task

class ChatAgent:
    def __init__(self, session: Session, user_id: UUID):
        self.session = session
        self.user_id = user_id
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL
        
        # Define available tools
        self.tools_definitions = [
            {
                "type": "function",
                "function": {
                    "name": "add_task",
                    "description": "Create a new todo task with a title and optional description.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "title": {
                                "type": "string",
                                "description": "The title of the task"
                            },
                            "description": {
                                "type": "string",
                                "description": "Optional details about the task"
                            }
                        },
                        "required": ["title"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "list_tasks",
                    "description": "List all tasks for the user.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "completed": {
                                "type": "boolean",
                                "description": "Filter by completion status (true for completed, false for incomplete)"
                            }
                        }
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "complete_task",
                    "description": "Mark a task as completed using its title or ID.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "task_identifier": {
                                "type": "string",
                                "description": "The task title (partial match supported) or exact ID"
                            }
                        },
                        "required": ["task_identifier"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "update_task",
                    "description": "Update a task's title or description.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "task_identifier": {
                                "type": "string",
                                "description": "The task title (partial match supported) or exact ID"
                            },
                            "title": {
                                "type": "string",
                                "description": "New title"
                            },
                            "description": {
                                "type": "string",
                                "description": "New description"
                            }
                        },
                        "required": ["task_identifier"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "delete_task",
                    "description": "Delete a task permanently.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "task_identifier": {
                                "type": "string",
                                "description": "The task title (partial match supported) or exact ID"
                            }
                        },
                        "required": ["task_identifier"]
                    }
                }
            }
        ]

    def _get_system_prompt(self) -> str:
        return """You are a helpful Todo Assistant. 
You help users manage their tasks using the available tools.
When specific tasks are referenced by name, try to find them using the tools.
Always confirm the action to the user in a friendly manner.
If the tool execution fails, explain why.
"""

    def process_message(self, history: List[Dict[str, str]]) -> str:
        """
        Process a message history and return the assistant's response.
        Handles tool calls automatically.
        """
        messages = [{"role": "system", "content": self._get_system_prompt()}] + history
        
        # First call to LLM
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=self.tools_definitions,
            tool_choice="auto"
        )
        
        response_message = response.choices[0].message
        
        # Handle tool calls
        if response_message.tool_calls:
            # Append the assistant's message with tool calls to history
            messages.append(response_message)
            
            for tool_call in response_message.tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)
                
                tool_output = {
                    "success": False, 
                    "message": "Unknown tool"
                }
                
                try:
                    if function_name == "add_task":
                        tool_output = add_task(self.session, self.user_id, **function_args)
                    elif function_name == "list_tasks":
                        tool_output = list_tasks(self.session, self.user_id, **function_args)
                    elif function_name == "complete_task":
                        tool_output = complete_task(self.session, self.user_id, **function_args)
                    elif function_name == "update_task":
                        tool_output = update_task(self.session, self.user_id, **function_args)
                    elif function_name == "delete_task":
                        tool_output = delete_task(self.session, self.user_id, **function_args)
                except Exception as e:
                    tool_output = {"success": False, "message": f"Error executing tool: {str(e)}"}
                
                # Append tool result to history
                messages.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": json.dumps(tool_output)
                })
            
            # Second call to LLM to generate final response
            final_response = self.client.chat.completions.create(
                model=self.model,
                messages=messages
            )
            return final_response.choices[0].message.content
            
        return response_message.content

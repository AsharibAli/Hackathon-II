"""
AI Agent configuration.
Configures the agent with MCP tools and system instructions.

[Task]: T033-T034, T042-T043, T051-T052, T057, T064-T065, T071, T078
[Spec]: F-001 to F-007
[Description]: Phase 5 enhanced agent with priority, tags, due dates, search, filter/sort, reminders, recurrence tools
"""
import json
import logging
from typing import List, Dict, Any, Optional
from uuid import UUID
from sqlmodel import Session
from openai import OpenAI, APIError, APIConnectionError, RateLimitError
from core.config import settings

logger = logging.getLogger(__name__)
from mcp.tools import (
    add_task, list_tasks, complete_task, update_task, delete_task,
    # Phase 5 MCP tools
    set_priority, filter_by_priority,
    add_tag, remove_tag, filter_by_tag,
    set_due_date, show_overdue,
    search_tasks,
    combined_filter, sort_tasks,
    set_reminder,
    set_recurrence,
)

class ChatAgent:
    def __init__(self, session: Session, user_id: UUID):
        self.session = session
        self.user_id = user_id
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL
        
        # Define available tools - Phase 5 enhanced
        self.tools_definitions = [
            # Core task operations
            {
                "type": "function",
                "function": {
                    "name": "add_task",
                    "description": "Create a new todo task. ALWAYS call this function when user wants to create a task - the system handles natural language date parsing automatically.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string", "description": "The title of the task"},
                            "description": {"type": "string", "description": "Optional details about the task"},
                            "priority": {"type": "string", "enum": ["low", "medium", "high"], "description": "Task priority level"},
                            "due_date": {"type": "string", "description": "Due date - accepts natural language like 'tomorrow', 'next Monday', 'next Friday', 'in 3 days', or ISO format. Pass the user's exact words."},
                            "tags": {"type": "array", "items": {"type": "string"}, "description": "List of tags to add"}
                        },
                        "required": ["title"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "list_tasks",
                    "description": "List all tasks with optional filters and sorting.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "completed": {"type": "boolean", "description": "Filter by completion status"},
                            "priority": {"type": "string", "enum": ["low", "medium", "high"], "description": "Filter by priority"},
                            "tag": {"type": "string", "description": "Filter by tag name"},
                            "overdue": {"type": "boolean", "description": "Show only overdue tasks"},
                            "sort_by": {"type": "string", "enum": ["created_at", "due_date", "priority", "title"], "description": "Sort field"},
                            "sort_order": {"type": "string", "enum": ["asc", "desc"], "description": "Sort order"}
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
                            "task_identifier": {"type": "string", "description": "The task title (partial match) or exact ID"}
                        },
                        "required": ["task_identifier"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "update_task",
                    "description": "Update a task's title, description, priority, due date, or recurrence.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "task_identifier": {"type": "string", "description": "The task title (partial match) or exact ID"},
                            "title": {"type": "string", "description": "New title"},
                            "description": {"type": "string", "description": "New description"},
                            "priority": {"type": "string", "enum": ["low", "medium", "high"], "description": "New priority"},
                            "due_date": {"type": "string", "description": "New due date"},
                            "recurrence": {"type": "string", "enum": ["none", "daily", "weekly", "monthly"], "description": "Recurrence pattern"}
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
                            "task_identifier": {"type": "string", "description": "The task title (partial match) or exact ID"}
                        },
                        "required": ["task_identifier"]
                    }
                }
            },
            # Phase 5: Priority tools (T033, T034)
            {
                "type": "function",
                "function": {
                    "name": "set_priority",
                    "description": "Set the priority of a task (e.g., 'set priority of Buy groceries to high').",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "task_identifier": {"type": "string", "description": "The task title (partial match) or exact ID"},
                            "priority": {"type": "string", "enum": ["low", "medium", "high"], "description": "Priority level"}
                        },
                        "required": ["task_identifier", "priority"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "filter_by_priority",
                    "description": "Show all tasks with a specific priority (e.g., 'show high priority tasks').",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "priority": {"type": "string", "enum": ["low", "medium", "high"], "description": "Priority level to filter by"}
                        },
                        "required": ["priority"]
                    }
                }
            },
            # Phase 5: Tag tools (T042, T043)
            {
                "type": "function",
                "function": {
                    "name": "add_tag",
                    "description": "Add a tag to a task (e.g., 'add tag work to Finish report').",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "task_identifier": {"type": "string", "description": "The task title (partial match) or exact ID"},
                            "tag": {"type": "string", "description": "Tag name to add"}
                        },
                        "required": ["task_identifier", "tag"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "remove_tag",
                    "description": "Remove a tag from a task.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "task_identifier": {"type": "string", "description": "The task title (partial match) or exact ID"},
                            "tag": {"type": "string", "description": "Tag name to remove"}
                        },
                        "required": ["task_identifier", "tag"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "filter_by_tag",
                    "description": "Show all tasks with a specific tag (e.g., 'show tasks tagged work').",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "tag": {"type": "string", "description": "Tag name to filter by"}
                        },
                        "required": ["tag"]
                    }
                }
            },
            # Phase 5: Due date tools (T051, T052)
            {
                "type": "function",
                "function": {
                    "name": "set_due_date",
                    "description": "Set the due date of a task. System automatically parses natural language dates - pass user's exact words.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "task_identifier": {"type": "string", "description": "The task title (partial match) or exact ID"},
                            "due_date": {"type": "string", "description": "Due date - accepts 'tomorrow', 'next Monday', 'next Friday', 'in 3 days', etc. Pass exactly what user said."}
                        },
                        "required": ["task_identifier", "due_date"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "show_overdue",
                    "description": "Show all overdue tasks (past due date and not completed).",
                    "parameters": {"type": "object", "properties": {}}
                }
            },
            # Phase 5: Search tool (T057)
            {
                "type": "function",
                "function": {
                    "name": "search_tasks",
                    "description": "Search tasks by keyword in title and description (e.g., 'search for grocery').",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "Search keyword"}
                        },
                        "required": ["query"]
                    }
                }
            },
            # Phase 5: Combined filter & sort tools (T064, T065)
            {
                "type": "function",
                "function": {
                    "name": "combined_filter",
                    "description": "Filter tasks with multiple criteria (e.g., 'show high priority pending tasks sorted by due date').",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "priority": {"type": "string", "enum": ["low", "medium", "high"], "description": "Filter by priority"},
                            "tag": {"type": "string", "description": "Filter by tag"},
                            "completed": {"type": "boolean", "description": "Filter by completion status"},
                            "overdue": {"type": "boolean", "description": "Filter for overdue tasks only"},
                            "sort_by": {"type": "string", "enum": ["created_at", "due_date", "priority", "title"], "description": "Sort field"},
                            "sort_order": {"type": "string", "enum": ["asc", "desc"], "description": "Sort order"}
                        }
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "sort_tasks",
                    "description": "Sort tasks by a specific field (e.g., 'sort by due date').",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "sort_by": {"type": "string", "enum": ["created_at", "updated_at", "due_date", "priority", "title"], "description": "Field to sort by"},
                            "sort_order": {"type": "string", "enum": ["asc", "desc"], "description": "Sort order (default: desc)"}
                        },
                        "required": ["sort_by"]
                    }
                }
            },
            # Phase 5: Reminder tool (T071)
            {
                "type": "function",
                "function": {
                    "name": "set_reminder",
                    "description": "Set a reminder for a task. Supports relative times like '1 hour before' (requires due date) or absolute times like 'tomorrow at 9am'.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "task_identifier": {"type": "string", "description": "The task title (partial match) or exact ID"},
                            "remind_at": {"type": "string", "description": "Reminder time - e.g., '1 hour before', '30 minutes before', 'tomorrow at 9am'. Pass exactly what user said."}
                        },
                        "required": ["task_identifier", "remind_at"]
                    }
                }
            },
            # Phase 5: Recurrence tool (T078)
            {
                "type": "function",
                "function": {
                    "name": "set_recurrence",
                    "description": "Set recurrence pattern for a task (e.g., 'make this task repeat weekly').",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "task_identifier": {"type": "string", "description": "The task title (partial match) or exact ID"},
                            "recurrence": {"type": "string", "enum": ["none", "daily", "weekly", "monthly"], "description": "Recurrence pattern"}
                        },
                        "required": ["task_identifier", "recurrence"]
                    }
                }
            }
        ]

    def _get_system_prompt(self) -> str:
        from datetime import datetime, timezone
        today = datetime.now(timezone.utc).strftime("%A, %B %d, %Y")

        return f"""You are a helpful Todo Assistant with advanced task management capabilities.

Today's date is: {today}

CRITICAL INSTRUCTIONS - FOLLOW EXACTLY:
1. When a user asks to create a task, IMMEDIATELY call the add_task function. DO NOT ask for clarification.
2. Pass ALL date expressions EXACTLY as the user stated them. The backend parses them automatically.
3. "next Monday", "tomorrow", "next Friday", "in 3 days" - ALL of these work. Just pass them directly.
4. For reminders like "1 hour before", pass "1 hour before" directly to set_reminder.
5. NEVER say "I couldn't parse the date" or ask for a specific date format. ALWAYS try the tool first.

You can help users:
- Create, update, complete, and delete tasks
- Set task priorities (low, medium, high)
- Add and remove tags for categorization
- Set due dates using natural language
- Set reminders for tasks
- Make tasks recurring (daily, weekly, monthly)
- Search and filter tasks

EXAMPLE - User says: "Add a high priority task called Finish report, due next Monday, tag it as work, set reminder 1 hour before"
YOU MUST:
1. Call add_task with: title="Finish report", priority="high", due_date="next Monday", tags=["work"]
2. Then call set_reminder with: task_identifier="Finish report", remind_at="1 hour before"

DO NOT ask the user to clarify "next Monday" - it works automatically.

When specific tasks are referenced by name, try to find them using the tools.
Always confirm the action to the user in a friendly manner after the tools succeed.
"""

    def process_message(self, history: List[Dict[str, str]]) -> str:
        """
        Process a message history and return the assistant's response.
        Handles tool calls automatically with multi-turn support.
        """
        messages = [{"role": "system", "content": self._get_system_prompt()}] + history
        max_iterations = 10  # Prevent infinite loops

        for iteration in range(max_iterations):
            try:
                # Call LLM with tools available
                logger.info(f"Calling OpenAI API (iteration {iteration + 1})")
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    tools=self.tools_definitions,
                    tool_choice="auto"
                )
                logger.info("OpenAI API call successful")

            except RateLimitError as e:
                logger.error(f"OpenAI rate limit exceeded: {e}")
                return "I'm currently experiencing high demand. Please try again in a moment."
            except APIConnectionError as e:
                logger.error(f"OpenAI connection error: {e}")
                return "I'm having trouble connecting to my AI service. Please try again."
            except APIError as e:
                logger.error(f"OpenAI API error: {e}")
                return "There was an issue with the AI service. Please try again."
            except Exception as e:
                logger.error(f"Unexpected error calling OpenAI: {e}", exc_info=True)
                return f"An unexpected error occurred: {str(e)}"

            response_message = response.choices[0].message

            # If no tool calls, return the text response
            if not response_message.tool_calls:
                return response_message.content or "I've completed your request."

            # Append the assistant's message with tool calls to history
            messages.append(response_message)

            # Execute each tool call
            for tool_call in response_message.tool_calls:
                function_name = tool_call.function.name
                try:
                    function_args = json.loads(tool_call.function.arguments)
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse tool arguments: {e}")
                    function_args = {}

                logger.info(f"Executing tool: {function_name} with args: {function_args}")

                tool_output = {
                    "success": False,
                    "message": "Unknown tool"
                }

                try:
                    tool_output = self._execute_tool(function_name, function_args)
                    logger.info(f"Tool {function_name} returned: success={tool_output.get('success', False)}")
                except Exception as e:
                    logger.error(f"Error executing tool {function_name}: {e}", exc_info=True)
                    tool_output = {"success": False, "message": f"Error executing tool: {str(e)}"}

                # Serialize tool output safely
                try:
                    tool_output_json = json.dumps(tool_output, default=str)
                except Exception as e:
                    logger.error(f"Failed to serialize tool output: {e}")
                    tool_output_json = json.dumps({"success": False, "message": "Failed to serialize result"})

                # Append tool result to history
                messages.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": tool_output_json
                })

            # Continue the loop to allow more tool calls or generate final response

        # If we hit max iterations, generate a final response
        return "I've processed your request. Please check your tasks to verify the changes."

    def _execute_tool(self, function_name: str, function_args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool by name with the given arguments."""
        # Tool mapping for cleaner dispatch
        tool_handlers = {
            # Core operations
            "add_task": add_task,
            "list_tasks": list_tasks,
            "complete_task": complete_task,
            "update_task": update_task,
            "delete_task": delete_task,
            # Phase 5: Priority
            "set_priority": set_priority,
            "filter_by_priority": filter_by_priority,
            # Phase 5: Tags
            "add_tag": add_tag,
            "remove_tag": remove_tag,
            "filter_by_tag": filter_by_tag,
            # Phase 5: Due dates
            "set_due_date": set_due_date,
            "show_overdue": show_overdue,
            # Phase 5: Search
            "search_tasks": search_tasks,
            # Phase 5: Filter & Sort
            "combined_filter": combined_filter,
            "sort_tasks": sort_tasks,
            # Phase 5: Reminders & Recurrence
            "set_reminder": set_reminder,
            "set_recurrence": set_recurrence,
        }

        if function_name in tool_handlers:
            return tool_handlers[function_name](self.session, self.user_id, **function_args)

        return {"success": False, "message": f"Unknown tool: {function_name}"}

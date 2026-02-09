"""
Main todo agent with Gemini 2.0 Flash.

This module defines the main AI agent for task management.
"""

from agents import Agent, OpenAIChatCompletionsModel, set_tracing_disabled, function_tool

from .gemini_client import gemini_client
from .guardrails import blocking_guardrail
from ..mcp.tools.task_tools import (
    create_task,
    list_tasks,
    get_task,
    complete_task,
    update_task,
    delete_task,
)


# Disable tracing in production
set_tracing_disabled(disabled=True)


# Wrap tools with function_tool decorator
create_task_tool = function_tool(create_task)
list_tasks_tool = function_tool(list_tasks)
get_task_tool = function_tool(get_task)
complete_task_tool = function_tool(complete_task)
update_task_tool = function_tool(update_task)
delete_task_tool = function_tool(delete_task)


# Main todo assistant agent
def get_instructions(ctx, agent):
    """Dynamic instructions that include user_id from context."""
    user_id = ctx.context.get("user_id") if ctx.context else None

    base_instructions = (
        "You are a helpful AI assistant that helps users manage their todo tasks through natural language. "
        "You can create, view, update, delete, and complete tasks for users. "
        "\n\n"
    )

    if user_id:
        base_instructions += f"IMPORTANT: The current user's ID is: {user_id}\n"
        base_instructions += "You MUST pass this user_id as the first parameter to ALL tool calls (create_task, list_tasks, get_task, complete_task, update_task, delete_task).\n\n"

    base_instructions += (
        "When users ask to create a task, extract the task title and optional description from their message. "
        "When users ask to view tasks, determine if they want all tasks, pending tasks, or completed tasks. "
        "When users ask to complete a task, identify the task by ID or by matching the title. "
        "When users ask to update a task, identify the task and the new information. "
        "When users ask to delete a task, identify the task and confirm before deletion. "
        "\n\n"
        "Always provide clear, friendly responses confirming actions taken. "
        "If a request is ambiguous, ask clarifying questions before taking action. "
        "Format task lists in a readable way with task IDs for easy reference."
    )

    return base_instructions


todo_agent = Agent(
    name="Todo Assistant",
    instructions=get_instructions,
    model=OpenAIChatCompletionsModel(
        model="gemini-2.0-flash",
        openai_client=gemini_client,
    ),
    input_guardrails=[blocking_guardrail],
    tools=[
        create_task_tool,
        list_tasks_tool,
        get_task_tool,
        complete_task_tool,
        update_task_tool,
        delete_task_tool,
    ],
)
